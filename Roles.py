from __future__ import annotations

from io import TextIOWrapper
import discord
import asyncio
import os
import json

        
class React_Role:
    def __init__(self, emoji: discord.Emoji|str, role: discord.Role, description: str = ""):
        if emoji is None or role is None or description is None:
            raise ValueError
        pass
        self.emoji: discord.Emoji|str = emoji
        self.role: discord.Role = role
        self.description: str = description
    pass

    def __eq__(self, other:React_Role|discord.Role):
        if isinstance(other, React_Role):
            return self.role == other.role and self.emoji == other.emoji
        elif isinstance(other, discord.Role):
            return self.role == other
        pass
        return False
    pass
    def __str__(self):
        return f'{self.emoji}: {self.role} - {self.description}'
    pass



class React_Group:
    def __init__(self, name:str,  roles: list[React_Role] = [], desc: str = "", flags: dict[str, bool] = {}):
        if name is None or roles is None or desc is None or flags is None:
            raise ValueError
        pass
        
        self.name: str = name
        self.roles: list[React_Role] = roles
        self.desc: str = desc
        self.flags: dict[str, bool] = flags
    pass

    def append(self, item: React_Role):
        self.roles.append(item)
    pass

    def __contains__(self, item: React_Role|discord.Role):
        if isinstance(item, (React_Role, discord.Role)):
            if item in self.roles:
                return True
            pass
        
        pass
        return False
    pass

    def __str__(self):
        retval = f"    name: {self.name},\n    roles: ["
        for i in self.roles:
            retval += "\n        "+str(i)+","
        retval += "],\n"
        retval += f"    desc: {self.desc},\n    flags: {str(self.flags)}"
        return retval
    pass

    @staticmethod
    def fromDict(d:dict) -> React_Group:
        roles = [React_Role(r.get("emoji"), r.get("role"), r.get("description", "")) for r in d.get("roles", [])]
        return React_Group(d.get("name"), roles, d.get("desc", ""), d.get("flags", {}))
    pass

class React_Conf:
    def __init__(self, guild: discord.Guild):
        self.guild: discord.Guild = guild
        self.opening_msg: str = "React to this message with one of the following reactions to get the associated role:"
        self.roles: list[React_Group] = []
        self.channel: discord.Channel|None = None
        self.message: discord.Message|discord.PartialMessage|None = None
    pass


    def __getitem__(self, key: str):
        if isinstance(key, str):
            return next(
                (obj for obj in self.roles if obj.name == key),
                None
            )
        pass
    pass
    def __contains__(self, item: React_Group|React_Role|discord.Role):
        if isinstance(item, React_Group):
            return item in self.roles
        elif isinstance(item, (React_Role, discord.Role)):
            for group in self.roles:
                if item in group.roles:
                    return True
                pass
            pass
            return False
        elif isinstance(item, str):
            return item in [i.name for i in self.roles]
        return False
    pass

    def __str__(self):
        retval = f"guild: {self.guild},\nopener:{self.opening_msg},\nroleGroups: ["
        for i in self.roles:
            retval += f"\n{str(i)},"
        retval += f"],\nchannel:{str(self.channel)},\nmessage:{str(self.message)}"
        return retval
    pass

    def to_json(self) -> dict:
        
        return {
            "opening_msg": self.opening_msg,
            "roles": [
                {
                    "name": group.name,
                    "desc": group.desc,
                    "flags": group.flags,
                    "roles": [
                        {
                            "emoji": role.emoji.id if isinstance(role.emoji, discord.Emoji) else role.emoji,
                            "role": role.role.id,
                            "description": role.description
                        } for role in group.roles
                    ]
                } for group in self.roles
            ],
            "channel": self.channel.id if self.channel is not None else None,
            "message": self.message.id if self.message is not None else None
        }   
    
    @staticmethod
    def from_json(f:TextIOWrapper, guild:discord.Guild):
        config = json.load(f)
        react_conf = React_Conf(guild)
        react_conf.opening_msg = config.get("opening_msg", "")
        react_conf.roles = [React_Group.fromDict(group) for group in config.get("roles", [])]
        if "channel" in config:
            react_conf.channel = guild.get_channel(config.get("channel"))
            if react_conf.channel is not None and "message" in config:
                react_conf.message = react_conf.channel.get_partial_message(config.get("message"))
            else:
                react_conf.message = None
            pass
        else:
            react_conf.channel = None
            react_conf.message = None
        
        return react_conf
    pass



pass