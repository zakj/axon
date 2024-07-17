# axon
*An attempt at rolling my own PKM system.*

This will eventually be a system of three parts:

- An LSP provider to get autocomplete on references to other pages in the PKM in whatever LSP-supporting editor/IDE I happen to be excited about that day.
- A Markdown-to-"block" transformer. A block is any top-level Markdown block element (paragraph, heading, etc.) or a list item at any depth.
- A simple UI that displays a journal by default, and allows querying to display a page and all the blocks (with their children) that reference it.

## Why

I've used various tools for personal knowledge management (glorified notes) over the years with varying success.
The most recent, and most successful so far, has been [Logseq][]. What I like best about it:

- It feels mostly like Markdown.
- Everything is a list, which saves me from deciding whether to use a list or to write in prose.
- The default view is a "journal," with one labeled entry per day. This makes it very easy to just write something, rather than worrying about the right place to file it.
- It supports `#tag`s and `[[wiki link]]`s to any page in the database. These links are attached to the "block," or list item where it's found.
- Notably, when viewing a given page, every block that links to it via tag or wiki link is displayed, including any child blocks of that block.

What I wish were better:

- The editing experience. I spend so much time in editors with good vim support that any other workflow inevitably frustrates me at some point. Logseq has *decent* vim support, which is just enough to lull me into a false sense of security.
- Once a page has many links to it (> 60ish?), those references are hidden and you have to click to display them. They also start to load slowly.

But mostly, I thought it would be fun to work on.

[Logseq]: https://logseq.com/
