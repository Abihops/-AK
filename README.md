# Abinav Khadka - Portfolio Website

A clean, modern portfolio website for showcasing your aerospace engineering projects and skills.

## Quick Start

1. Open `index.html` in your browser to preview
2. Customize the content (see below)
3. Deploy to GitHub Pages, Vercel, or Netlify (all free!)

## How to Customize

### Add Your Photos/Images

1. Create an `images` folder in this directory
2. Add project images (recommended: 800x600px or larger)
3. Replace the placeholder divs in `index.html` with actual images:

```html
<!-- Change this: -->
<div class="project-placeholder">
    <span>🌙</span>
    <p>Add project image</p>
</div>

<!-- To this: -->
<img src="images/your-project.jpg" alt="Project Name">
```

### Update Content

All content is in `index.html`. Update:
- Hero section text
- About section paragraphs
- Project descriptions and bullet points
- Skills list
- Contact information

### Add More Projects

Copy a project card block and customize:

```html
<div class="project-card">
    <div class="project-image">
        <img src="images/new-project.jpg" alt="Project Name">
    </div>
    <div class="project-info">
        <div class="project-tags">
            <span class="tag">Tag 1</span>
            <span class="tag">Tag 2</span>
        </div>
        <h3>Project Title</h3>
        <p class="project-role">Your Role | Date</p>
        <p>Project description...</p>
        <ul class="project-details">
            <li>Achievement 1</li>
            <li>Achievement 2</li>
        </ul>
        <div class="project-tech">
            <span>Tool 1</span>
            <span>Tool 2</span>
        </div>
    </div>
</div>
```

## Deploying Your Site (Free!)

### Option 1: GitHub Pages (Recommended)

1. Create a GitHub account if you don't have one
2. Create a new repository named `abinavk.github.io` (use your username)
3. Upload all files from this `portfolio` folder
4. Go to Settings → Pages → Enable GitHub Pages
5. Your site will be live at `https://abinavk.github.io`

### Option 2: Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project" → Import your portfolio repo
4. Deploy! You'll get a free `.vercel.app` URL

### Option 3: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Drag and drop this entire folder onto the page
3. Done! You'll get a free `.netlify.app` URL

## File Structure

```
portfolio/
├── index.html      # Main HTML file
├── styles.css      # All styling
├── script.js       # Animations and interactions
├── README.md       # This file
└── images/         # Add your project images here
    ├── c3-payload.jpg
    ├── solarcar.jpg
    └── ...
```

## Tips for Great Project Images

- **CAD Screenshots**: Export high-quality renders from SolidWorks/Inventor
- **CFD Results**: Screenshot your ANSYS visualizations
- **Team Photos**: Show your team working on projects
- **Technical Diagrams**: System architecture, CAD assemblies
- **Testing Photos**: Document your testing setups

## Customization Ideas

- Change the accent color in `styles.css` (search for `--accent-primary`)
- Add more sections (education, certifications, etc.)
- Add a downloadable resume link
- Embed videos of your projects

---

Good luck with the job search! 🚀

