# saheb.github.com

My personal website.

## Local development

### Prerequisites

- Python 3
- [Hugo extended](https://gohugo.io/installation/): `brew install hugo`

Ruby, Jekyll, and Bundle are not required. The root website is static HTML; only the blog is built by
Hugo.

### Build and preview the full site

The build script mirrors `.github/workflows/deploy.yml`: it copies the root static site into `_site/`,
includes current root HTML pages and project assets, builds the Hugo blog into `_site/blog/`, and
removes files left over from older builds. For local preview, Hugo generates blog asset and post URLs
under `http://localhost:4000/blog/`.

```bash
cd /Users/saheb/home/saheb.github.com
bash scripts/build-site.sh
python3 -m http.server 4000 --directory _site
```

Open <http://localhost:4000>. Stop the server with `Ctrl+C`.

To use another port, give the build and server the same value:

```bash
SITE_BASE_URL=http://localhost:8080 bash scripts/build-site.sh
python3 -m http.server 8080 --directory _site
```

Run `bash scripts/build-site.sh` again after changing root files or blog content. The Python server can
remain running while you rebuild. Root HTML files and files under `project-assets/` can be previewed
before they are added to Git. Other new files must be added to Git before the script includes them.

### Blog-only development with live reload

```bash
cd /Users/saheb/home/saheb.github.com/blog
hugo server
```

The blog will be available at <http://localhost:1313>.

### Add a new blog post

```bash
cd /Users/saheb/home/saheb.github.com/blog
hugo new content posts/my-post.md
```
