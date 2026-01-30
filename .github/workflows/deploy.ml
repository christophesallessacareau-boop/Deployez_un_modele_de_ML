name: Deploy FastAPI to Hugging Face Space

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Prepare clean git repo
        run: |
          rm -rf .git
          git init
          git config user.email "actions@github.com"
          git config user.name "github-actions"
          git add .
          git commit -m "Deploy FastAPI app"

      - name: Push to Hugging Face Space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          HF_SPACE_REPO: ${{ vars.HF_SPACE_REPO }}
        run: |
          git remote add hf https://user:${HF_TOKEN}@huggingface.co/spaces/${HF_SPACE_REPO}
          git push hf HEAD:main --force
