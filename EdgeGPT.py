"""
Main.py
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import ssl
import sys
import uuid
from enum import Enum
from pathlib import Path
from typing import Generator
from typing import Literal
from typing import Optional
from typing import Union

import certifi
import httpx
import websockets.client as websockets
from BingImageCreator import ImageGenAsync
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.live import Live
from rich.markdown import Markdown

DELIMITER = "\x1e"


# Generate random IP between range 13.104.0.0/14
FORWARDED_IP = (
    f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
)

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not_A Brand";v="99", "Microsoft Edge";v="110", "Chromium";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"109.0.1518.78"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": FORWARDED_IP,
}

HEADERS_INIT_CONVER = {
    "authority": "edgeservices.bing.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"110.0.1587.69"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
    "x-edge-shopping-flag": "1",
    "x-forwarded-for": FORWARDED_IP,
}

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class NotAllowedToAccess(Exception):
    pass


class ConversationStyle(Enum):
    creative = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "h3imaginative",
        "travelansgnd",
        "dv3sugg",
        "clgalileo",
        "gencontentv3",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
    ]
    balanced = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "galileo",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
    ]
    precise = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "galileo",
        "dv3sugg",
        "responseos",
        "e2ecachewrite",
        "cachewriteext",
        "nodlcpcwrite",
        "travelansgnd",
        "h3precise",
        "clgalileo",
    ]


CONVERSATION_STYLE_TYPE = Optional[
    Union[ConversationStyle, Literal["creative", "balanced", "precise"]]
]


def _append_identifier(msg: dict) -> str:
    """
    Appends special character to end of message to identify end of message
    """
    # Convert dict to json string
    return json.dumps(msg) + DELIMITER


def _get_ran_hex(length: int = 32) -> str:
    """
    Returns random hex string
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(length))


class _ChatHubRequest:
    """
    Request object for ChatHub
    """

    def __init__(
        self,
        conversation_signature: str,
        client_id: str,
        conversation_id: str,
        invocation_id: int = 0,
    ) -> None:
        self.struct: dict = {}

        self.client_id: str = client_id
        self.conversation_id: str = conversation_id
        self.conversation_signature: str = conversation_signature
        self.invocation_id: int = invocation_id

    def update(
        self,
        prompt: str,
        conversation_style: CONVERSATION_STYLE_TYPE,
        options: list | None = None,
    ) -> None:
        """
        Updates request object
        """
        if options is None:
            options = [
                "deepleo",
                "enable_debug_commands",
                "disable_emoji_spoken_text",
                "enablemm",
            ]
        if conversation_style:
            if not isinstance(conversation_style, ConversationStyle):
                conversation_style = getattr(ConversationStyle, conversation_style)
            options = conversation_style.value
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "allowedMessageTypes": [
                        "Chat",
                        "InternalSearchQuery",
                        "InternalSearchResult",
                        "Disengaged",
                        "InternalLoaderMessage",
                        "RenderCardRequest",
                        "AdsQuery",
                        "SemanticSerp",
                        "GenerateContentQuery",
                        "SearchQuery",
                    ],
                    "sliceIds": [
                        "chk1cf",
                        "nopreloadsscf",
                        "winlongmsg2tf",
                        "perfimpcomb",
                        "sugdivdis",
                        "sydnoinputt",
                        "wpcssopt",
                        "wintone2tf",
                        "0404sydicnbs0",
                        "405suggbs0",
                        "scctl",
                        "330uaugs0",
                        "0329resp",
                        "udscahrfon",
                        "udstrblm5",
                        "404e2ewrt",
                        "408nodedups0",
                        "403tvlansgnd",
                    ],
                    "traceId": _get_ran_hex(32),
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                },
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }
        self.invocation_id += 1


class _Conversation:
    """
    Conversation API
    """

    def __init__(
        self,
        cookies: dict,
        proxy: str | None = None,
    ) -> None:
        self.struct: dict = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.proxy = proxy
        proxy = (
            proxy
            or os.environ.get("all_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or None
        )
        if proxy is not None and proxy.startswith("socks5h://"):
            proxy = "socks5://" + proxy[len("socks5h://") :]
        self.session = httpx.Client(
            proxies=proxy,
            timeout=30,
            headers=HEADERS_INIT_CONVER,
        )
        for cookie in cookies:
            self.session.cookies.set(cookie["name"], cookie["value"])

        # Send GET request
        response = self.session.get(
            url=os.environ.get("BING_PROXY_URL")
            or "https://edgeservices.bing.com/edgesvc/turing/conversation/create",
        )
        if response.status_code != 200:
            response = self.session.get(
                "https://edge.churchless.tech/edgesvc/turing/conversation/create",
            )
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)
            print(response.url)
            raise Exception("Authentication failed")
        try:
            self.struct = response.json()
        except (json.decoder.JSONDecodeError, NotAllowedToAccess) as exc:
            raise Exception(
                "Authentication failed. You have not been accepted into the beta.",
            ) from exc
        if self.struct["result"]["value"] == "UnauthorizedRequest":
            raise NotAllowedToAccess(self.struct["result"]["message"])


class _ChatHub:
    """
    Chat API
    """

    def __init__(self, conversation: _Conversation) -> None:
        self.wss: websockets.WebSocketClientProtocol | None = None
        self.request: _ChatHubRequest
        self.loop: bool
        self.task: asyncio.Task
        self.request = _ChatHubRequest(
            conversation_signature=conversation.struct["conversationSignature"],
            client_id=conversation.struct["clientId"],
            conversation_id=conversation.struct["conversationId"],
        )

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str,
        cookies: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()
        # Check if websocket is closed
        self.wss = await websockets.connect(
            wss_link,
            extra_headers=HEADERS,
            max_size=None,
            ssl=ssl_context,
        )
        await self._initial_handshake()
        # Construct a ChatHub request
        self.request.update(
            prompt=prompt,
            conversation_style=conversation_style,
            options=options,
        )
        # Send request
        await self.wss.send(_append_identifier(self.request.struct))
        final = False
        draw = False
        while not final:
            objects = str(await self.wss.recv()).split(DELIMITER)
            for obj in objects:
                if obj is None or not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") != 2 and raw:
                    yield False, response
                elif response.get("type") == 1 and response["arguments"][0].get(
                    "messages",
                ):
                    try:
                        if not draw:
                            resp_txt = response["arguments"][0]["messages"][0][
                                "adaptiveCards"
                            ][0]["body"][0].get("text")
                        yield False, resp_txt
                    except Exception as exc:
                        print(exc)
                        if not draw:
                            continue
                        for item in cookies:
                            if item["name"] == "_U":
                                U = item["value"]
                        async with ImageGenAsync(U, True) as image_generator:
                            images = await image_generator.get_images(
                                response["arguments"][0]["messages"][0]["text"],
                            )
                        cache = resp_txt
                        resp_txt = (
                            cache
                            + "\n![image0]("
                            + images[0]
                            + ")\n![image1]("
                            + images[1]
                            + ")\n![image0]("
                            + images[2]
                            + ")\n![image3]("
                            + images[3]
                            + ")"
                        )
                        yield False, resp_txt
                elif response.get("type") == 2:
                    if draw:
                        cache = response["item"]["messages"][1]["adaptiveCards"][0][
                            "body"
                        ][0]["text"]
                        response["item"]["messages"][1]["adaptiveCards"][0]["body"][0][
                            "text"
                        ] = (cache + resp_txt)
                    final = True
                    yield True, response

    async def _initial_handshake(self) -> None:
        await self.wss.send(_append_identifier({"protocol": "json", "version": 1}))
        await self.wss.recv()

    async def close(self) -> None:
        """
        Close the connection
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()


class Chatbot:
    """
    Combines everything to make it seamless
    """

    def __init__(
        self,
        cookies: dict = None,
        proxy: str | None = None,
        cookie_path: str = None,
    ) -> None:
        if cookies is None:
            cookies = {}
        if cookie_path is not None:
            try:
                with open(cookie_path, encoding="utf-8") as f:
                    self.cookies = json.load(f)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Cookie file not found") from exc
        else:
            self.cookies = cookies
        self.proxy: str | None = proxy
        self.chat_hub: _ChatHub = _ChatHub(
            _Conversation(self.cookies, self.proxy),
        )

    async def ask(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        options: dict = None,
    ) -> dict:
        """
        Ask a question to the bot
        """
        async for final, response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            options=options,
            cookies=self.cookies,
        ):
            if final:
                return response
        await self.chat_hub.wss.close()
        return None

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        async for response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            raw=raw,
            options=options,
            cookies=self.cookies,
        ):
            yield response

    async def close(self) -> None:
        """
        Close the connection
        """
        await self.chat_hub.close()

    async def reset(self) -> None:
        """
        Reset the conversation
        """
        await self.close()
        self.chat_hub = _ChatHub(_Conversation(self.cookies))


async def _get_input_async(
    session: PromptSession = None,
    completer: WordCompleter = None,
) -> str:
    """
    Multiline input function.
    """
    return await session.prompt_async(
        completer=completer,
        multiline=True,
        auto_suggest=AutoSuggestFromHistory(),
    )


def _create_session() -> PromptSession:
    kb = KeyBindings()

    @kb.add("enter")
    def _(event):
        buffer_text = event.current_buffer.text
        if buffer_text.startswith("!"):
            event.current_buffer.validate_and_handle()
        else:
            event.current_buffer.insert_text("\n")

    @kb.add("escape")
    def _(event):
        if event.current_buffer.complete_state:
            # event.current_buffer.cancel_completion()
            event.current_buffer.text = ""

    return PromptSession(key_bindings=kb, history=InMemoryHistory())


def _create_completer(commands: list, pattern_str: str = "$"):
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


async def async_main(args: argparse.Namespace) -> None:
    """
    Main function
    """
    print("Initializing...")
    print("Enter `alt+enter` or `escape+enter` to send a message")
    bot = Chatbot(proxy=args.proxy, cookies=args.cookies)
    session = _create_session()
    completer = _create_completer(["!help", "!exit", "!reset"])
    initial_prompt = args.prompt

    while True:
        print("\nYou:")
        if initial_prompt:
            question = initial_prompt
            print(question)
            initial_prompt = None
        else:
            question = (
                input()
                if args.enter_once
                else await _get_input_async(session=session, completer=completer)
            )
        print()
        if question == "!exit":
            break
        if question == "!help":
            print(
                """
            !help - Show this help message
            !exit - Exit the program
            !reset - Reset the conversation
            """,
            )
            continue
        if question == "!reset":
            await bot.reset()
            continue
        print("Bot:")
        if args.no_stream:
            print(
                (
                    await bot.ask(
                        prompt=question,
                        conversation_style=args.style,
                        wss_link=args.wss_link,
                    )
                )["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"],
            )
        else:
            wrote = 0
            if args.rich:
                md = Markdown("")
                with Live(md, auto_refresh=False) as live:
                    async for final, response in bot.ask_stream(
                        prompt=question,
                        conversation_style=args.style,
                        wss_link=args.wss_link,
                    ):
                        if not final:
                            if wrote > len(response):
                                print(md)
                                print(Markdown("***Bing revoked the response.***"))
                            wrote = len(response)
                            md = Markdown(response)
                            live.update(md, refresh=True)
            else:
                async for final, response in bot.ask_stream(
                    prompt=question,
                    conversation_style=args.style,
                    wss_link=args.wss_link,
                ):
                    if not final:
                        if not wrote:
                            print(response, end="", flush=True)
                        else:
                            print(response[wrote:], end="", flush=True)
                        wrote = len(response)
                print()
    await bot.close()


def main() -> None:
    print(
        """
        EdgeGPT - A demo of reverse engineering the Bing GPT chatbot
        Repo: github.com/acheong08/EdgeGPT
        By: Antonio Cheong

        !help for help

        Type !exit to exit
    """,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--enter-once", action="store_true")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--rich", action="store_true")
    parser.add_argument(
        "--proxy",
        help="Proxy URL (e.g. socks5://127.0.0.1:1080)",
        type=str,
    )
    parser.add_argument(
        "--wss-link",
        help="WSS URL(e.g. wss://sydney.bing.com/sydney/ChatHub)",
        type=str,
        default="wss://sydney.bing.com/sydney/ChatHub",
    )
    parser.add_argument(
        "--style",
        choices=["creative", "balanced", "precise"],
        default="balanced",
    )
    parser.add_argument(
        "--cookie-file",
        type=str,
        default=os.environ.get("COOKIE_FILE", ""),
        required=False,
        help="Cookie file used for authentication (defaults to COOKIE_FILE environment variable)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="",
        required=False,
        help="prompt to start with",
    )
    args = parser.parse_args()
    if args.cookie_file == "":
        parser.print_help()
        parser.exit(
            1,
            "ERROR: use --cookie-file or set the COOKIE_FILE environment variable",
        )
    try:
        args.cookies = json.loads(Path(args.cookie_file).read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Could not open cookie file: {exc}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()