# Documents, layout, and accessibility

A frontend is an interactive document used through different screens, input devices, languages, and assistive technologies. Relay's task editor is correct only if a person can perceive its state, operate its controls, understand errors, and recover from mistakes. A visually convincing screenshot proves little about those properties.

## Start with meaning

HTML describes structure and semantics. A `button` participates in keyboard activation, focus, forms, and accessibility APIs. A styled `div` does not acquire those behaviors because it looks like a button. Headings establish a navigable outline; `nav`, `main`, and other landmarks describe regions. Links navigate; buttons perform actions. Native semantics reduce the amount of interaction code you must invent and maintain.

```html
<form>
  <label for="title">Task title</label>
  <input id="title" name="title" required maxlength="120"
         aria-describedby="title-help">
  <p id="title-help">Use a short description of the work.</p>
  <button type="submit">Create task</button>
</form>
```

A placeholder is not a durable label. A browser's `required` validation improves feedback but does not protect the backend; callers can bypass the browser entirely. When an asynchronous submission fails, preserve entered data, associate field errors with controls, and move or announce focus deliberately. Avoid repeatedly stealing focus during background refreshes.

## CSS is a constraint system

The cascade determines which declarations win through origin, importance, layers, specificity, and order. Inheritance passes selected computed values to descendants. A layout bug may come from a competing rule rather than the rule you are editing. Developer tools show computed styles and the winning declaration; guessing with more `!important` rules creates future ambiguity.

The box model includes content, padding, borders, and margins. `box-sizing: border-box` often makes declared dimensions easier to reason about, but overflow still depends on content and minimum sizes. Long URLs, translated text, and zoom reveal assumptions hidden by tidy sample data.

Flexbox distributes items mainly along one dimension; Grid expresses two-dimensional tracks and placement. Choose based on relationships, not fashion. A toolbar is naturally a flex row that may wrap. A page with aligned sidebar/main tracks often fits Grid. Intrinsic sizing allows content to influence layout, which is useful until an unbreakable string or default minimum prevents shrinking.

```css
.workspace {
  display: grid;
  grid-template-columns: minmax(12rem, 18rem) minmax(0, 1fr);
  gap: 1rem;
}
@media (max-width: 48rem) {
  .workspace { grid-template-columns: 1fr; }
}
```

`minmax(0, 1fr)` permits the main track to shrink below content's intrinsic minimum; it does not automatically wrap every child. Test actual overflow. Responsive design should adapt to available space and content needs, not a list of assumed device models. Use flexible widths, sensible maximum line lengths, and images that fit their containers.

## Accessibility is state engineering

Keyboard users need visible focus and a logical focus order. A modal requires controlled focus entry, containment while open where appropriate, and restoration on close. Screen readers need programmatically exposed names, roles, states, and relationships. Color alone cannot carry error meaning. Motion-sensitive users need respected reduced-motion preferences. Touch targets and contrast affect many users, not just those with diagnosed impairments.

ARIA supplements missing semantics; it does not implement behavior. Adding `role="button"` to a `div` still leaves keyboard interactions for you to implement. Prefer native controls and tested accessible primitives for complex widgets. Automated accessibility tools catch some problems; manual keyboard, zoom, and screen-reader checks catch others.

## Failure-driven inspection

Relay's save button disappears on a narrow viewport because a fixed-width sidebar and main panel exceed the screen. Inspect the layout constraints and overflow rather than reducing font size. A form reports “saved” visually but a screen reader receives no update: use an appropriate status announcement without making every render noisy. A custom dropdown works with a mouse but traps keyboard focus: the missing piece is an interaction model, not another CSS rule.

In developer tools, inspect the DOM, computed style, box dimensions, accessibility tree, console, and network panel as separate evidence sources. The DOM says what exists; the accessibility tree says what assistive technology can perceive; the screenshot says what was painted. They can disagree.

## Exercises

1. **Check:** Why is a clickable `div` more work than a button?
2. **Debug:** A flex child overflows despite `width: 100%`. Inspect intrinsic minimums, padding, and parent constraints before proposing a fix.
3. **Implementation:** Build the form above with server error feedback. Use it with keyboard only, at 200% zoom, and with a long translated label.
4. **Design:** Specify focus behavior for creating a task in a modal and then deleting that task.
5. **Interview:** Explain how semantic HTML improves both accessibility and maintainability.

<details><summary>Review criteria</summary>

The form has a stable accessible name for each control, a visible focus indicator, preserved input after failure, and an understandable success/error announcement. The modal returns focus to a meaningful surviving element when its original trigger no longer exists.

</details>

## Further reading and connections

[HTML Living Standard](https://html.spec.whatwg.org/), [WAI tutorials](https://www.w3.org/WAI/tutorials/), and [MDN CSS layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout) provide authoritative foundations. Connect to [browser rendering](browser-internals.md), [React forms](react-mental-model.md), and [behavior testing](testing.md).
