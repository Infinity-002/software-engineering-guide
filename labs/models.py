"""Deterministic educational models. No persistence or thread-safety guarantee."""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import math
import unittest


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float):
        if expected_items <= 0 or not 0 < false_positive_rate < 1:
            raise ValueError("Use a positive capacity and a probability in (0, 1)")
        self.m = math.ceil(-expected_items * math.log(false_positive_rate) / math.log(2) ** 2)
        self.k = max(1, round(self.m / expected_items * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def positions(self, key: str):
        encoded = key.encode("utf-8")
        for seed in range(self.k):
            digest = hashlib.sha256(seed.to_bytes(8, "big") + encoded).digest()
            yield int.from_bytes(digest, "big") % self.m

    def add(self, key: str) -> None:
        for position in self.positions(key):
            self.bits[position // 8] |= 1 << (position % 8)

    def might_contain(self, key: str) -> bool:
        return all(self.bits[p // 8] & (1 << (p % 8)) for p in self.positions(key))


@dataclass
class TokenBucket:
    capacity: int
    rate_per_second: int
    last_ms: int = 0

    def __post_init__(self):
        if self.capacity <= 0 or self.rate_per_second <= 0:
            raise ValueError("Capacity and refill rate must be positive")
        self.tokens = Fraction(self.capacity)

    def consume(self, now_ms: int, cost: int = 1) -> bool:
        if cost <= 0 or cost > self.capacity:
            raise ValueError("Cost must fit in one bucket")
        # This is one sequential model operation. A real shared limiter must
        # perform refill, decision, and deduction atomically at its authority.
        effective_now = max(self.last_ms, now_ms)
        self.tokens = min(Fraction(self.capacity), self.tokens +
                          Fraction((effective_now - self.last_ms) * self.rate_per_second, 1000))
        self.last_ms = effective_now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True


class LeaseAuthority:
    def __init__(self):
        self.epoch = 0
        self.holder = None
        self.expires_ms = 0

    def acquire(self, holder: str, now_ms: int, ttl_ms: int):
        if ttl_ms <= 0:
            raise ValueError("TTL must be positive")
        if self.holder is not None and now_ms < self.expires_ms:
            return None
        self.epoch += 1
        self.holder = holder
        self.expires_ms = now_ms + ttl_ms
        return self.epoch

    def renew(self, holder: str, epoch: int, now_ms: int, ttl_ms: int) -> bool:
        if ttl_ms <= 0:
            raise ValueError("TTL must be positive")
        if (holder, epoch) != (self.holder, self.epoch) or now_ms >= self.expires_ms:
            return False
        self.expires_ms = now_ms + ttl_ms
        return True

    def release(self, holder: str, epoch: int) -> bool:
        if (holder, epoch) != (self.holder, self.epoch):
            return False
        self.holder = None
        return True


class FencedRegister:
    def __init__(self):
        self.highest_fence = 0
        self.value = None

    def write(self, fence: int, value: str) -> bool:
        # This check and write are one atomic model transition. Equal-token
        # operations need their own ordering/idempotency policy in real systems.
        if fence < self.highest_fence:
            return False
        self.highest_fence = fence
        self.value = value
        return True


class MechanismTests(unittest.TestCase):
    def test_bloom_inserted_keys_are_never_absent(self):
        bloom = BloomFilter(1000, 0.01)
        for i in range(1000):
            bloom.add(f"present-{i}")
        self.assertTrue(all(bloom.might_contain(f"present-{i}") for i in range(1000)))
        false_positives = sum(bloom.might_contain(f"absent-{i}") for i in range(10000))
        print(f"\nBloom: {bloom.m} bits, {bloom.k} hashes, {false_positives}/10000 false positives")
        # Deterministic smoke bound, not a mathematical probability guarantee.
        self.assertLess(false_positives, 300)

    def test_bloom_duplicate_insert_is_unchanged(self):
        bloom = BloomFilter(10, 0.1)
        bloom.add("same")
        before = bytes(bloom.bits)
        bloom.add("same")
        self.assertEqual(before, bytes(bloom.bits))

    def test_bucket_burst_refill_and_capacity(self):
        bucket = TokenBucket(20, 5)
        self.assertTrue(bucket.consume(0, 20))
        self.assertFalse(bucket.consume(0))
        self.assertTrue(bucket.consume(3000, 15))
        self.assertFalse(bucket.consume(3000))
        self.assertTrue(bucket.consume(100000, 20))
        self.assertFalse(bucket.consume(100000))

    def test_backward_observation_does_not_create_tokens(self):
        bucket = TokenBucket(1, 1)
        self.assertTrue(bucket.consume(1000))
        self.assertFalse(bucket.consume(500))
        self.assertFalse(bucket.consume(1500))
        self.assertTrue(bucket.consume(2000))

    def test_new_fence_rejects_resumed_old_holder(self):
        authority, resource = LeaseAuthority(), FencedRegister()
        old = authority.acquire("A", 0, 10000)
        self.assertIsNone(authority.acquire("B", 9000, 10000))
        new = authority.acquire("B", 11000, 10000)
        self.assertTrue(resource.write(new, "new result"))
        self.assertFalse(resource.write(old, "stale result"))
        self.assertEqual(resource.value, "new result")

    def test_expiry_alone_does_not_reject_at_resource(self):
        authority, resource = LeaseAuthority(), FencedRegister()
        old = authority.acquire("A", 0, 10000)
        authority.acquire("B", 11000, 10000)
        # Resource has not observed B's fence. This deliberately demonstrates
        # the limitation of maximum-seen fencing, not a safe lease validation.
        self.assertTrue(resource.write(old, "arrived before newer fence"))

    def test_stale_release_and_renew_cannot_change_new_lease(self):
        authority = LeaseAuthority()
        old = authority.acquire("A", 0, 10000)
        new = authority.acquire("B", 11000, 10000)
        self.assertFalse(authority.release("A", old))
        self.assertFalse(authority.renew("A", old, 12000, 10000))
        self.assertEqual((authority.holder, authority.epoch), ("B", new))

    def test_expired_holder_must_reacquire(self):
        authority = LeaseAuthority()
        old = authority.acquire("A", 0, 10)
        self.assertFalse(authority.renew("A", old, 10, 10))
        self.assertGreater(authority.acquire("A", 10, 10), old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
