#
# Fenix protocol messages
#
# © Copyright 2020 by luk3yx and piesquared
#

# Optional __future__ import for testing
from __future__ import annotations

from typing import Dict, Type, Union, Any

from fenixclient import _protocolCore

class _BaseProtocol(_protocolCore.BaseMessage): #type: ignore
    pass

outgoingMessages: _protocolCore.ProtocolHelper = _protocolCore.ProtocolHelper()

@outgoingMessages.add('signIn')
class SignIn(_BaseProtocol):
    email: str
    password: str

@outgoingMessages.add('signUp')
class SignUp(_BaseProtocol):
    email: str
    username: str
    password: str

@outgoingMessages.add('createChannel')
class CreateChannel(_BaseProtocol):
    serverID: int
    name: str

@outgoingMessages.add('sendMessage')
class SendMessage(_BaseProtocol):
    channelID: int
    contents: str

@outgoingMessages.add('editMessage')
class EditMessage(_BaseProtocol):
    messageID: int
    contents: str

@outgoingMessages.add('deleteMessage')
class DeleteMessage(_BaseProtocol):
    messageID: int

@outgoingMessages.add('addReaction')
class AddReaction(_BaseProtocol):
    messageID: int
    reaction: str

@outgoingMessages.add('removeReaction')
class RemoveReaction(_BaseProtocol):
    messageID: int
    reaction: int

@outgoingMessages.add('changeServerPermission')
class ChangeServerPermission(_BaseProtocol):
    permission: str
    value: bool
    userID: int
    serverID: int
    actor: int

@outgoingMessages.add('changechannelPermission')
class ChangechannelPermission(_BaseProtocol):
    permission: str
    value: bool
    userID: int
    channelID: int
    actor: int

@outgoingMessages.add('getPerms')
class GetPerms(_BaseProtocol):
    userID: int
    serverID: int

@outgoingMessages.add('getPermsList')
class GetPermsList(_BaseProtocol):
    userID: int
    serverID: int

@outgoingMessages.add('hasChannelPermission')
class HasChannelPermission(_BaseProtocol):
    permission: str
    userID: int
    channelID: int

@outgoingMessages.add('hasServerPermission')
class HasServerPermission(_BaseProtocol):
    permission: str
    userID: int
    channelID: int

@outgoingMessages.add('getRoles')
class GetRoles(_BaseProtocol):
    userID: int
    serverID: int

@outgoingMessages.add('getRolesList')
class GetRolesList(_BaseProtocol):
    userID: int
    serverID: int

@outgoingMessages.add('joinRoles')
class JoinRoles(_BaseProtocol):
    userID: int
    serverID: int
    roleID: int
    actor: int

@outgoingMessages.add('createServer')
class CreateServer(_BaseProtocol):
    userID: int
    name: str

@outgoingMessages.add('getServer')
class GetServer(_BaseProtocol):
    serverID: int

@outgoingMessages.add('getServers')
class GetServers(_BaseProtocol):
    serverID: int

@outgoingMessages.add('getServersList')
class GetServersList(_BaseProtocol):
    serverID: int