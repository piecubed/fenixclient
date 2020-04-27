# © (Copyright) 2020 by piesquared.
import websockets
from typing import Dict, Any, Callable, Iterator, Union, List
import json
import asyncio
from fenixclient import _protocolCore
import datetime
import sys

class _BaseProtocol(_protocolCore.BaseMessage): #type: ignore
    pass

_incomingMessages: _protocolCore.ProtocolHelper = _protocolCore.ProtocolHelper()

@_incomingMessages.add('authUser')
class AuthUser(_BaseProtocol):
    id: int
    username: str
    email: str
    settings: Dict[str, Any]
    token: str
    usernameHash: int
    createdAt: datetime.datetime
    verified: bool
    servers: Dict[str, Dict[str, str]]

_outgoingMessages: _protocolCore.ProtocolHelper = _protocolCore.ProtocolHelper()

@_outgoingMessages.add('signIn')
class SignIn(_BaseProtocol):
    email: str
    password: str

@_outgoingMessages.add('signUp')
class SignUp(_BaseProtocol):
    email: str
    username: str
    password: str

@_outgoingMessages.add('createChannel')
class CreateChannel(_BaseProtocol):
    serverID: int
    name: str

@_outgoingMessages.add('sendMessage')
class SendMessage(_BaseProtocol):
    channelID: int
    contents: str

@_outgoingMessages.add('editMessage')
class EditMessage(_BaseProtocol):
    messageID: int
    contents: str

@_outgoingMessages.add('deleteMessage')
class DeleteMessage(_BaseProtocol):
    messageID: int

@_outgoingMessages.add('addReaction')
class AddReaction(_BaseProtocol):
    messageID: int
    reaction: str

@_outgoingMessages.add('removeReaction')
class RemoveReaction(_BaseProtocol):
    messageID: int
    reaction: int

@_outgoingMessages.add('changeServerPermission')
class ChangeServerPermission(_BaseProtocol):
    permission: str
    value: bool
    userID: int
    serverID: int
    actor: int

@_outgoingMessages.add('changechannelPermission')
class ChangechannelPermission(_BaseProtocol):
    permission: str
    value: bool
    userID: int
    channelID: int
    actor: int

@_outgoingMessages.add('getPerms')
class GetPerms(_BaseProtocol):
    userID: int
    serverID: int

@_outgoingMessages.add('getPermsList')
class GetPermsList(_BaseProtocol):
    userID: int
    serverID: int

@_outgoingMessages.add('hasChannelPermission')
class HasChannelPermission(_BaseProtocol):
    permission: str
    userID: int
    channelID: int

@_outgoingMessages.add('hasServerPermission')
class HasServerPermission(_BaseProtocol):
    permission: str
    userID: int
    channelID: int

@_outgoingMessages.add('getRoles')
class GetRoles(_BaseProtocol):
    userID: int
    serverID: int

@_outgoingMessages.add('getRolesList')
class GetRolesList(_BaseProtocol):
    userID: int
    serverID: int

@_outgoingMessages.add('joinRoles')
class JoinRoles(_BaseProtocol):
    userID: int
    serverID: int
    roleID: int
    actor: int

@_outgoingMessages.add('createServer')
class CreateServer(_BaseProtocol):
    userID: int
    name: str

@_outgoingMessages.add('getServer')
class GetServer(_BaseProtocol):
    serverID: int

@_outgoingMessages.add('getServers')
class GetServers(_BaseProtocol):
    serverID: int

@_outgoingMessages.add('getServersList')
class GetServersList(_BaseProtocol):
    serverID: int

class Client:
    """
    Base fenix client.
    """
    __queue: Dict[int, asyncio.Lock]  = {}
    __lastID = 0
    __websocket: websockets.WebSocketClientProtocol
    __responses: Dict[int, Union[_BaseProtocol, None]]
    __listeners: Dict[str, List[Callable[[_BaseProtocol], Any]]]

    async def __connect(self) -> None:
        self.__websocket = await websockets.connect('wss://bloblet.com:3300')

    async def __parseMessage(self, message: Dict[str, Any]) -> None:
        if message['type'] == 'message':
            await self.__informClient(message)
        try:
            self.__responses[message['id']] = _incomingMessages.types[message['type']](message)
        except KeyError:
            print(f"Recieved a a unknown protocol, {message['type']}", file=sys.stderr)
        finally:
            self.__responses[message['id']] = None
            self.__queue[message['id']].release()


    async def __informClient(self, message: Dict[str, Any]) -> None:
        protocol = await self.__incomingMessagesCaster(message['type'], **message)

        for i in self.__listeners[message['type']]:
            i(protocol)


    def addListener(self, *names: str) -> Callable[[Callable[[_BaseProtocol], None]], Callable[[_BaseProtocol], None]]:
        """
        A decorator to add packet types.
        ```
        @client.addListener('packetName')
        def handlePacketName(message: BaseProtocol):
            ...
        ```
        """

        def wrapper(func: Callable[[_BaseProtocol], None]) -> Callable[[_BaseProtocol], None]:
            for name in names:
                if name in self.__listeners.keys():
                    self.__listeners[name].append(func)
                else:
                    self.__listeners[name] = [func]

            return func

        return wrapper

    async def __rawSend(self, payload: _BaseProtocol) -> None:
        await self.__websocket.send(payload.dumps())

    async def __send(self, payload: _BaseProtocol) -> Union[_BaseProtocol, None]:
        lock = asyncio.Lock()
        self.__lastID += 1
        id = self.__lastID
        self.__queue[self.__lastID] = lock

        await self.__rawSend(payload)

        # This waits until this lock is released, and when it is, it will get the message and parse it.
        lock.acquire()

        # We need to "garbage collect" the lock and the response.
        del self.__queue[id]
        response = self.__responses[id]
        del self.__responses[id]

        return response

    async def __outgoingMessagesCaster(self, type: str, **kwargs: Any) -> _BaseProtocol:
        """Casts into a protocol.

        Parameters
        ----------
        type : str
            The type this should return.

        **kwargs : Dict[str, Any]
            The args to make the protocol with.
        Returns
        -------
        _BaseProtocol
            Returns a subclass of _BaseProtocol

        Raises
        ------
        TypeError
            Raises TypeError if ``type`` is not in the _outgoingMessages var.
        """

        try:
            result: _BaseProtocol = _outgoingMessages.types[type](kwargs)
            return result
        except:
            raise TypeError

    async def __incomingMessagesCaster(self, type: str, **kwargs: Any) -> _BaseProtocol:
        """Casts into a protocol.

        Parameters
        ----------
        type : str
            The type this should return.

        **kwargs : Dict[str, Any]
            The args to make the protocol with.
        Returns
        -------
        _BaseProtocol
            Returns a subclass of _BaseProtocol

        Raises
        ------
        TypeError
            Raises TypeError if ``type`` is not in the _incomingMessages var.
        """

        try:
            result: _BaseProtocol = _incomingMessages.types[type](kwargs)
            return result
        except:
            raise TypeError

    async def login(self, email: str, password: str) -> Union[AuthUser, None]:
        """
        Attempts to log into a user.

        Parameters
        ----------
        email : str
            The email of the user
        password : str
            The password of the user

        Returns
        -------
        Union[AuthUser, None]
            If the server sends a unknown protocol (this should never happen), None is returned.
        """

        login = self.__outgoingMessagesCaster('login', email=email, password=password)
        response: Union[AuthUser, None] = await self.__send(login)

        return response

    async def run(self) -> None:
        """
        This function runs forever, run this with

        ```
        loop = asyncio.get_event_loop()
        loop.run_forever(client.run())
        ```.
        """
        await self.__connect()

        async for message in self.__websocket:
            await self.__parseMessage(json.loads(message))

class InvalidType(Exception):
    pass