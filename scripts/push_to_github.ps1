param(
  [string]$remoteUrl = 'https://github.com/medc-0/voice-sound-ai.git'
)

Write-Host "This script will set the branch to 'main', add remote origin and push. Make sure you have permissions to the repo and that your credentials are configured."

git branch -M main
git remote remove origin 2>$null; # ignore if doesn't exist
git remote add origin $remoteUrl
git add -A
git commit -m "Initial commit from local desktop" 2>$null || Write-Host "No changes to commit or commit failed"
git push -u origin main

Write-Host "Done. If push failed, check authentication or repo permissions."
