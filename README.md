# Akaneqwq's Homepage

This repository hosts the statically exported build of [PRISM](https://github.com/Akaneqwq/PRISM) — a personal academic homepage built with Next.js.

The live site is deployed via GitHub Pages at [https://akaneqwq.github.io/](https://akaneqwq.github.io/).

## Update the site

1. In the PRISM project, update content and build:

   ```bash
   npm run build
   ```

2. Copy the generated `out/` directory into this repository:

   ```bash
   cp -R path/to/PRISM/out/. .
   ```

3. Make sure `.nojekyll` exists (it prevents GitHub Pages from running Jekyll, which would otherwise ignore the `_next` directory and break the page):

   ```bash
   touch .nojekyll
   ```

4. Commit and push:

   ```bash
   git add -A && git commit -m "deploy: update site" && git push origin master
   ```

GitHub Pages picks up changes on the `master` branch automatically within a couple of minutes.
