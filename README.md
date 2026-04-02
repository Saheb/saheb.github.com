# saheb.github.com

My personal website.

## Local Development

### Prerequisites
- Hugo (extended): `brew install hugo`

### Serve the site
```bash
# Build the blog (outputs to _site/blog/)
cd blog && hugo && cd ..

# Serve the entire site from _site/
python3 -m http.server 4000 --directory _site
```

The site will be available at http://localhost:4000

### Blog only (with live reload)
```bash
cd blog && hugo server
```

The blog will be available at http://localhost:1313

### Add a new post
```bash
cd blog && hugo new content my-post.md
```
