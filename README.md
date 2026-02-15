# Floof Farm - Static Website

ADGA Registered Nigerian Dwarf and Toggenburg Dairy Goats  
https://floof.farm

## Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) v0.112.0+ (uses extended features)

## Local Development

```bash
hugo server
```

Visit http://localhost:1313

## Build for Production

```bash
hugo --minify
```

Output goes to `public/` directory.

## Deploy to Netlify

1. Push this repo to GitHub/GitLab
2. Connect to Netlify
3. Build command: `hugo --minify`
4. Publish directory: `public`
5. Set environment variable: `HUGO_VERSION=0.142.0`

Or add a `netlify.toml`:

```toml
[build]
  command = "hugo --minify"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.142.0"
```

## Deploy to Cloudflare Pages

1. Push this repo to GitHub/GitLab
2. Connect to Cloudflare Pages
3. Framework preset: Hugo
4. Build command: `hugo --minify`
5. Build output directory: `public`
6. Environment variable: `HUGO_VERSION=0.142.0`

## Contact Form Setup

The contact form uses [Formspree](https://formspree.io/). To activate:

1. Create a free Formspree account
2. Create a new form with email destination: k8chapman@gmail.com
3. Replace `YOUR_FORM_ID` in `content/contact.md` with your Formspree form ID
4. The form subject is set to "** Floof Farm Goats **"

## Image Migration

Images currently reference `https://floof.farm/wp-content/uploads/*`. To self-host:

1. Download the uploads directory from WordPress
2. Place files in `static/uploads/`
3. Find/replace `https://floof.farm/wp-content/uploads/` with `/uploads/` across all content files

## Structure

```
content/
├── _index.md          # Home page
├── does/              # Doe profiles (17 goats)
├── bucks/             # Buck profiles (7 goats)
├── sold/              # Sold goats (4)
├── wethers/           # Wethers (1)
├── for-sale/          # Current sales listings (5)
├── blog/              # Blog posts (34)
├── genetics/          # Genetics content
├── breeding-schedules/ # Yearly breeding schedules
├── shows.md           # Show results
├── contact.md         # Contact form
├── sales-policy.md    # Sales policy
└── gestation-calculator.md  # Interactive gestation calculator
```

## Theme

Custom theme in `themes/floof/` with warm, earthy colors (greens, browns, cream). Mobile responsive with goat profile cards and blog listing.
