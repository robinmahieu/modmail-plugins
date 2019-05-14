# Autorole

This plugin makes it possible to auto-assign roles when a user joins your server.

## Installation

To use this plugin, use this command in your Modmail server: `plugin add papiersnipper/modmail-plugins/autorole`

## Commands

| name      | usage              | example          | permission         |description                             |
|-----------|--------------------|------------------|--------------------|----------------------------------------|
| setrole   | setrole rolename   | setrole Member   | Administrator [4]  | Gives this role to all new members     |
| giveroles | giveroles rolename | giveroles Member | Administrator [4]  | Gives this role to all existing members |

> The bot will only accept role names, so pinging the role **will not** work!

## Permissions

The bot doesn't need additional permissions, but keep in mind that the role it's assigning needs to be lower in rank than the bot's role.