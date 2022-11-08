# md2docs

Sync local text files to your Google Docs.

## Installation

Use `pipx` to try out md2docs!

```bash
pipx install git+https://github.com/gavindsouza/md2docs.git
```

## Usage

Create a settings.json file under `~/.md2docs` that looks like:

```json
[
    {
        "source": "/home/gavin/Notes/Team Feedback.md",
        "target": "1GoocLXXXXXXXXXXXXXXXXXGzIFd866waPxxY",
    }
]
```

`source` is the name of the file you want to sync with a Google Doc. `target` is the Document ID which can be found in URL of a document you create eg: [https://docs.google.com/document/d/**1GoocLXXXXXXXXXXXXXXXXXGzIFd866waPxxY**/edit#]

After you've got this setup, just run `md2docs` in your terminal. It'll ask you to sign in to your Google Account - which will be a one time setup.

Now, you can add this to your crontab and md2docs will sync your local notes with Google Docs at whatever frequency you want :)

## ToDo

- [ ] Full Markdown support
