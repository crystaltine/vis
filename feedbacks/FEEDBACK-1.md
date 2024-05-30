# Feedback on sprint 1

## Some useful git commands
I used these commands to get a quick read on what everyone did. Then I delved into specific files for a closer look.
* git log --all --graph --oneline --pretty=format:"%C(auto)%<|(20,trunc)%an%<(10)%h%<(60,trunc)%s%d"
* git log --all --numstat --oneline --author <author>

## Overall score: 10/10

You guys have built some really cool stuff! I'm looking forward to getting a demo!

One thing you can improve on is your git management. Take a look at your git log and you'll see what I mean. When
you put up a PR, make sure you look at your commits first and curate them to be as clear as you can. Play around with
"git rebase -i", that's the main tool for rewriting commits. Also, see if you can figure out where all the merge
commits are coming from and learn to avoid them!
