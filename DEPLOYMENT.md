# Deployment Setup Instructions

## 1. GitHub Repository Setup

1. Push your code to GitHub
2. Go to your repository settings
3. Navigate to "Pages" section
4. Under "Source", select "GitHub Actions"

## 2. Custom Domain Configuration

### Step 1: Update CNAME file
Replace `yourdomain.com` in `docs/CNAME` with your actual domain name.

### Step 2: Update mkdocs.yml
Replace the following placeholders in `mkdocs.yml`:
- `site_url: https://yoursite.com` → `site_url: https://yourdomain.com`
- `repo_url: https://github.com/yourusername/grapegeek` → your actual repo URL
- Update the GitHub link in the `extra.social` section

### Step 3: DNS Configuration
Point your domain to GitHub Pages by adding these DNS records at your domain registrar:

**For apex domain (yourdomain.com):**
```
Type: A
Name: @
Value: 185.199.108.153

Type: A  
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153
```

**For www subdomain (optional):**
```
Type: CNAME
Name: www
Value: yourusername.github.io
```

## 3. Deployment Process

1. Push changes to the `main` branch
2. GitHub Actions will automatically build and deploy your MkDocs site
3. Your site will be available at your custom domain within a few minutes
4. SSL certificate will be automatically provisioned by GitHub

## 4. Adding New Content

### Generated Articles
When you generate new grape variety articles:
```bash
python main.py grape <variety_name> --type technical
```

Copy the generated files from `output/articles/` to `docs/varieties/` and commit.

### Generated Region Research  
When you generate region research:
```bash
python main.py region <region_name>
```

Copy the generated files from `output/regions/` to `docs/regions/` and commit.

## 5. Local Development

To preview your MkDocs site locally:
```bash
pip install mkdocs-material mkdocs-git-revision-date-localized-plugin
mkdocs serve
```

Visit http://localhost:8000 to preview changes.

## Troubleshooting

- **Custom domain not working**: Check DNS propagation (can take up to 48 hours)
- **Build failing**: Check GitHub Actions logs in the "Actions" tab of your repository
- **Content not updating**: Ensure you've committed and pushed changes to the `main` branch