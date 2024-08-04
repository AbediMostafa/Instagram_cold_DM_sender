from instagrapi import Client
from instagrapi.exceptions import ProxyAddressIsBlocked, ChallengeRequired, UserNotFound, FeedbackRequired, \
    ClientNotFoundError, ClientForbiddenError, ClientConnectionError, PleaseWaitFewMinutes, LoginRequired, \
    TwoFactorRequired, ChallengeUnknownStep
from .InstagramErrorHandler import InstagramErrorHandler

from script.extra.helper import pause


class InstagramMobileMiddleware:
    login_attempt = 0
    error_handler = None

    def __init__(self, account):
        self.account = account
        self.client = Client()
        self.error_handler = InstagramErrorHandler(self.account)
        self.client.delay_range = [1, 3]
        self.login_attempt = 0

    @staticmethod
    def try_except(func):
        def nested_func(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)

            except ProxyAddressIsBlocked as e:
                self.error_handler.handle_proxy_blocked_exception(str(e))

            except (ChallengeRequired, ChallengeUnknownStep) as e:
                self.error_handler.handle_account_challenging_exception(str(e))

            except UserNotFound as e:
                self.account.add_cli(f'Lead username not found: {str(e)}')

            except ClientForbiddenError as e:
                self.error_handler.handle_client_forbidden_exception(str(e))

            except FeedbackRequired as e:
                self.error_handler.handle_feedback_required_exception(str(e))

            except ClientNotFoundError as e:
                self.error_handler.handle_client_not_found_exception(str(e))

            except ClientConnectionError as e:
                self.error_handler.handle_client_connection_error(str(e))

            except PleaseWaitFewMinutes as e:
                self.error_handler.handle_wait_a_few_minutes_exception(str(e))

            except TwoFactorRequired as e:
                self.error_handler.handle_two_factor_required_exception(str(e))

            except LoginRequired as e:
                self.error_handler.handle_login_required_exception(str(e))

            except Exception as e:
                exception_type = type(e)
                exception_class = e.__class__.__name__
                print(f"Exception type: {exception_type}")
                print(f"Exception class: {exception_class}")
                print(str(e))
                raise e
                # self.error_handler.handle_general_exceptions(str(e))

        return nested_func

    @try_except
    def change_name(self, name):
        self.client.account_edit(full_name=name)

    @try_except
    def change_username(self, name):
        self.client.account_edit(username=name)

    @try_except
    def change_bio(self, bio):
        self.client.account_edit(biography=bio)

    @try_except
    def change_avatar(self, path):
        info = self.client.account_change_picture(path)
        self.account.set('profile_pic_url', info.profile_pic_url)

    @try_except
    def delete_initial_posts(self):
        medias = self.client.user_medias(str(self.client.user_id))

        for media in medias:
            self.client.media_delete(media.id)
            pause(2, 5)

    @try_except
    def user_id_from_username(self, lead):
        user = self.client.user_info_by_username_v1(lead.username)
        lead.update_instagram_id(user.pk)
        return lead.username

    @try_except
    def follow(self, lead):
        self.client.user_follow(lead.instagram_id)

    @try_except
    def direct_send(self, user_ids, text):
        return self.client.direct_send(user_ids=user_ids, text=text)

    @try_except
    def direct_send_video(self, path, thread_id):
        return self.client.direct_send_video(path=path, thread_ids=[thread_id])

    @try_except
    def photo_upload(self, path, caption):
        self.client.photo_upload(path=path, caption=caption)

    @try_except
    def video_upload(self, path, caption):
        self.client.video_upload(path=path, caption=caption)

    @try_except
    def direct_threads(self, amount=20):
        return self.client.direct_threads(amount=amount, thread_message_limit=20)

    @try_except
    def login(self, *args, **kwargs):
        self.client.login(*args, **kwargs)

    @try_except
    def get_timeline_feed(self):
        self.client.get_timeline_feed()
