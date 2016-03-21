jive-python-scripts
===================

Python scripts to perform several admin tasks on jive via jive v3 REST apis

Recommended Python version : 3.5.1

Note : This script originally was meant for 2.7. I have now moved all to python v3.5.1. If you find something not working with the new version, let me know. I will push the fixes soon

As a Jive developer and admin, I have to perform several tasks to debug issues on our internal jive instance, or run spikes to test rest apis for a jive app to be developed.
I love python and so end up writing a scripts to perform actions on jive using rest apis.

I have tried to put some of those random scripts in this repo and will keep updating.

I have done some random refactoring on the script before checkin as some of these were writen an year back.
So if they give an error, do let me know. Coz I have not tested every refactored method while checkin, but have run it sometime back on our prod instance. The concept behind each action is still valid.

Feel free to use these to understand jive rest apis and debug jive issues on your instance.

**Scripts contain following Jive actions:**

- Endorse expertise for a user
- Associate a group with user's stream (follow group)
- Add user as member to a group
- Force users to follow a group in email watches stream (if present. this was for our custom streamonce)
- Get group followers
- Get group members
- Delete membership
- Check streams and receive emails status of each stream of a user
- Create a new stream for user
- Get all jive system properties
- Create jive system properties
- Destroy jive system properties
- Get all groups on jive instance
- Get all private and secret groups
- remove all users from a group
- Get user photos / avatars
- Download all content of a group in pdf format
- Get groups owned by a user
- Send direct message
- Run-as-feature
- Disable user
- Get list of groups with their latest activity
- Search group by url name
- Create content in place
- Update group
- Get delete group object
- Create static
- Remove all associations of  group with a user (streams)
- Update user

Though jive cloud admin console does not have system property view, the above mentioned action related to system properties work via jive rest API on cloud too

