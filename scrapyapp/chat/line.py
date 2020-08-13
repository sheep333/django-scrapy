from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
import logging

from django.conf import settings
from django.db import DataError

from .models import LineInputData


logger = logging.getLogger(__name__)


class LineBotModule:
    line_bot_api = LineBotApi(settings.CHANEL_ACCESS_TOKEN)
    handler = WebhookHandler(settings.CHANNEL_SECRET)

    def __init__(self, request):
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        self._execute(signature, body)
        logger.info("Request body: " + body)

    def _execute(self, body, signature):
        # handle webhook body
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("Invalid signature. Please check your channel access token/channel secret.")

    def _message_data_save(self, event):
        try:
            LineInputData(
                user_id=event.source.user,
                timestamp=event.timestamp,
                message=event.message.as_json_string(),
                question=self._check_question(event),
                answer=event.message.text,
            ).save()
            logger.info(f"Saved line data. Event:{event}")
        except Exception:
            logger.error(f"Can't save line data. Event:{event}")
            raise DataError

    def _check_question(self, event):
        if '' in event.message.text:
            return LineInputData.QUESTIONS_NAME[0]

    # handlerにTextメッセージを受け取った時に行う処理を追加
    # デコレータの第一引数のeventには.models.eventsにイベントを指定 ex) FollowEvent, AccountLinkEvent等
    # デコレータの第二引数のmessageには.models.messages.Messageのメッセージ型を指定
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(self, event):
        self._message_data_save(event)
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )
        text = event.message.text

        if text == 'profile':
            if isinstance(event.source, SourceUser):
                profile = self.line_bot_api.get_profile(event.source.user_id)
                self.line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='Display name: ' +
                                        profile.display_name),
                        TextSendMessage(text='Status message: ' +
                                        profile.status_message)
                    ]
                )
            else:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Bot can't use profile API without user ID"))
        elif text == 'bye':
            if isinstance(event.source, SourceGroup):
                self.line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                self.line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                self.line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Leaving group'))
                self.line_bot_api.leave_room(event.source.room_id)
            else:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Bot can't leave from 1:1 chat"))
        elif text == 'confirm':
            confirm_template = ConfirmTemplate(text='Do it?', actions=[
                MessageAction(label='Yes', text='Yes!'),
                MessageAction(label='No', text='No!'),
            ])
            template_message = TemplateSendMessage(
                alt_text='Confirm alt text', template=confirm_template)
            self.line_bot_api.reply_message(event.reply_token, template_message)
        elif text == 'buttons':
            buttons_template = ButtonsTemplate(
                title='My buttons sample', text='Hello, my buttons', actions=[
                    URIAction(label='Go to line.me', uri='https://line.me'),
                    PostbackAction(label='ping', data='ping'),
                    PostbackAction(label='ping with text', data='ping', text='ping'),
                    MessageAction(label='Translate Rice', text='米')
                ])
            template_message = TemplateSendMessage(
                alt_text='Buttons alt text', template=buttons_template)
            self.line_bot_api.reply_message(event.reply_token, template_message)
        elif text == 'carousel':
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(text='hoge1', title='fuga1', actions=[
                    URIAction(label='Go to line.me', uri='https://line.me'),
                    PostbackAction(label='ping', data='ping')
                ]),
                CarouselColumn(text='hoge2', title='fuga2', actions=[
                    PostbackAction(label='ping with text', data='ping', text='ping'),
                    MessageAction(label='Translate Rice', text='米')
                ]),
            ])
            template_message = TemplateSendMessage(
                alt_text='Carousel alt text', template=carousel_template)
            self.line_bot_api.reply_message(event.reply_token, template_message)
        elif text == 'image_carousel':
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                    action=DatetimePickerAction(label='datetime',
                                                                data='datetime_postback',
                                                                mode='datetime')),
                ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                    action=DatetimePickerAction(label='date',
                                                                data='date_postback',
                                                                mode='date'))
            ])
            template_message = TemplateSendMessage(
                alt_text='ImageCarousel alt text', template=image_carousel_template)
            self.line_bot_api.reply_message(event.reply_token, template_message)
        elif text == 'imagemap':
            pass
        elif text == 'flex':
            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://example.com/cafe.jpg',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=URIAction(uri='http://example.com', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                        # review
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(
                                    size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(
                                    size='sm', url='https://example.com/grey_star.png'),
                                IconComponent(
                                    size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(
                                    size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(
                                    size='sm', url='https://example.com/grey_star.png'),
                                TextComponent(text='4.0', size='sm', color='#999999', margin='md', flex=0)
                            ]
                        ),
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Place',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text='Shinjuku, Tokyo',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Time',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text="10:00 - 23:00",
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # callAction, separator, websiteAction
                        SpacerComponent(size='sm'),
                        # callAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='CALL', uri='tel:000000'),
                        ),
                        # separator
                        SeparatorComponent(),
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(
                                label='WEBSITE', uri="https://example.com")
                        )
                    ]
                ),
            )
            message = FlexSendMessage(alt_text="hello", contents=bubble)
            self.line_bot_api.reply_message(
                event.reply_token,
                message
            )
        elif text == 'quick_reply':
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='Quick reply',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=PostbackAction(label="label1", data="data1")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="label2", text="text2")
                            ),
                            QuickReplyButton(
                                action=DatetimePickerAction(label="label3", data="data3",
                                                            mode="date")
                            ),
                            QuickReplyButton(
                                action=CameraAction(label="label4")
                            ),
                            QuickReplyButton(
                                action=CameraRollAction(label="label5")
                            ),
                            QuickReplyButton(
                                action=LocationAction(label="label6")
                            ),
                        ])))
        elif text == "liff":
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='https://line.me/R/app/1615588360-p4vKyQMV'),
                ]
            )
        elif text == "purchase":
            previous_bot_message = "question"
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='商品の購入ですね！\nそれではいくつか質問させてもらいますね。'),
                    TextSendMessage(text='これから購入のための情報をお聞きしますが、'),
                    ConfirmTemplate(
                        action=[
                            MessageAction(
                                label='chat',
                                text='ちゃっとで答える'
                            ),
                            MessageAction(
                                label='webpage',
                                text='Webページで入力する'
                            ),
                        ]
                    )
                ]
            )
        elif previous_bot_message == "question" and text == "chat":
            previous_bot_message = "name"
            self.line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='ありがとうございます！！'),
                    TextSendMessage(text='さっそくお名前を教えてもらえますか？'),

                ]
            )
