# 2. Push Data Changes to GitHub

Date: 2020-04-15

## Status

Accepted

## Context

The API for publishing release notes is not advanced and is just a giant blob of JSON containing every release in the database. A GitLab Job runs on a schedule and reads this blob, splits it into a file per release, and commits those changes to a GitHub repo. This job is slow and is something else to maintain and monitor separate from Nucleus. So the decision was between improving the API to only send the releases that had changed since the last sync, or to push changes to GitHub as soon as the're made. The latter has the advantages of happening very quickly after the change is saved, and having the context of the Nucleus user who made the change which can also be recorded in the Git commit.

## Decision

We've decided to go with pushing changes directly to GitHub via the GitHub API and using an async worker system to do it. The async system chosen was [Spinach][].

## Consequences

This means that we can retire the GitLab job consuming the API, the API itself, and the current [release-notes repo][]. However, we do now have to monitor the activity of the nucleus worker more closely to ensure that it is not encountering errors. It does have retry capabilities if a commit fails, and it records activity in a model which can be seen in the Django Admin. The error reporting and recovery capabilities are as follows:

1. The tasks retry 8 times with exponential backoff (usually around 20min total)
2. Failed tasks don't set an `ack` flag on the log DB entry, and are then retried again if they sit unacked for at least an hour, and this happens hourly for up to 5 times
3. We can see the failed ones in the admin
4. We'll have Sentry alerts for every time they fail
5. We can add other alerts for when they hit max retries and will go into the hourly retries

We thought about how we might use Dead Man's Snitch here but there won't be anything that happens regularly enough. It's all triggered by user action, which may not be every day.

[Spinach]: https://spinach.readthedocs.io/en/stable/index.html
[release-notes repo]: https://github.com/mozilla/release-notes/
