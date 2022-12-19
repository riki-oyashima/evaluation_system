from ev_sys_pwa.app.utils.database.data_class import Authority, InputNumberStep


class Message:
    DEFAULT = ""
    MEMBER_INIT = "まずは自己評価を入力しましょう。"
    MEMBER_WAIT_MANAGER = "上司の評価を待ちましょう。"
    MEMBER_ONE_ON_ONE_INITIAL = "上司と評価の認識合わせをしましょう。"
    MANAGER_INIT = "{target_member}さんの評価をしましょう。"

    MESSAGE_DICT = {
        Authority.Manager.value: {
            InputNumberStep.init.value: MANAGER_INIT,
        },
        Authority.Member.value: {
            InputNumberStep.init.value: MEMBER_INIT,
            InputNumberStep.user_input.value: MEMBER_WAIT_MANAGER,
            InputNumberStep.manager_input.value: MEMBER_ONE_ON_ONE_INITIAL,
        }
    }

    def get_message(self, authority, input_number, **kwargs):
        print(authority, input_number, kwargs)
        return self.MESSAGE_DICT.get(authority, {}).get(input_number, self.DEFAULT).format(**kwargs)
