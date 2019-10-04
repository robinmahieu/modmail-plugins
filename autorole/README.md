<div align="center">
    <img  src="https://i.imgur.com/7DNRLHT.png" align="center">
    <p><strong><i>Auto-assign a role to a user when they join your server.</i></strong></p>
</div>

## Installation

To install this plugin, use this command in your Modmail server: `plugin add autorole`.

## Commands

| name           | usage              | example               | permission        | description                                         |
| -------------- | ------------------ | --------------------- | ----------------- | --------------------------------------------------- |
| autorole clear | autorole clear     | autorole clear        | Administrator [4] | Clear the default role(s).                          |
| autorole give  | autorole give role | autorole give @Member | Administrator [4] | Give the joined member all currently set roles.     |
| autorole set   | autorole set role  | autorole set @Member  | Administrator [4] | Set the default role(s) a member gets when joining. |

## Permissions

The bot doesn't need additional permissions, but keep in mind that the role it's assigning needs to be lower in rank than the bot's role.
