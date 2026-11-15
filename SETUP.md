# Setup (5 minutes)

1. Put everything in this folder into your profile repository (`deprimus01/deprimus01`), keeping the `.github` folder, the `assets` folder and `README.md` together. Commit and push to `main`.

2. Open the repo's **Actions** tab. The **Update profile** and **Contribution snake** workflows start on that first push. If they don't, open each one and click **Run workflow**.
3. After about a minute your real stats, language chart, recent repositories and the contribution snake appear. They refresh every 6 hours after that.
4. If a workflow fails with a permissions error, go to **Settings, Actions, General, Workflow permissions** and choose **Read and write permissions**, then run it again.
5. Set your GitHub bio from `BIO.txt`.

**Important:** the `.github` folder is hidden on most computers, and copying files by hand often skips it. Copy with `cp -a` (or drag the whole folder in a terminal), then run `ls -a` and check that `.github` is there before you push. Without it the stats cards and the snake never go live.

How the numbers work: nothing is typed in by hand. `profile_stats.py` reads your public data from the GitHub API on every run and redraws the cards. Contribution and pull request counts are added automatically when the workflow runs with its built-in token.

Light mode: every graphic ships with a `-light.svg` variant that GitHub shows automatically to visitors using the light theme.
