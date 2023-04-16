---
title: Scripture Semantic Search
emoji: 📖
colorFrom: blue
colorTo: blue
sdk: gradio
sdk_version: 3.23.0
app_file: app.py
pinned: false
---


## Local Setup
### Obtain the repo locally and open its root folder
To potentially contribute
```shell
git clone git@github.com:pkiage/ChatBot-Bible.git
```
or
```shell
gh repo clone gh repo clone pkiage/ChatBot-Bible
```

To just deploy locally
Download ZIP

### (optional) Setup virtual environment:
```shell
python -m venv venv
```

### (optional) Activate virtual environment:
If using Unix based OS run the following in terminal:

```shell
.\venv\bin\activate
```

If using Windows run the following in terminal:

```shell
.\venv\Scripts\activate
```

Install requirements by running the following in terminal:

```shell
pip install -r requirements.txt
```

## Initial Data 
- [thiagobodruk/bible](https://github.com/thiagobodruk/bible)
- [seven1m/bible_api](https://github.com/seven1m/bible_api)

## Gradio Space Setup (Hugging Face)

- https://huggingface.co/docs/hub/spaces-config-reference
- https://huggingface.co/docs/hub/spaces-github-actions
- https://git-lfs.com/

```shell
git remote add space https://huggingface.co/spaces/pkiage/scripture-semantic-search

git push --force space main
```
- When [syncing with Hugging Face via Github Actions](https://huggingface.co/docs/hub/spaces-github-actions) the [User Access Token](https://huggingface.co/docs/hub/security-tokens) created on Hugging Face (HF) should have write access
- Run space from main branch since running from [other branches currently isn't suppported](https://discuss.huggingface.co/t/is-it-possible-to-run-apps-off-of-non-main-branches-in-a-space/18086)
- Ensure integrate remote changes (git pull) before push to HF space (```git push --force space main```)

## Git LFS
```shell
 git lfs track "*.parquet" "*.pkl" "*.json"
 ```