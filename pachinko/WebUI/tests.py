from utils import add_cash_payout

def test_add_cash_payout():
    test_data = [
        {'date':'2014-05-27', 'time_of_win': '13:45', 'win_number':1, 'renchan':0, 'spin_count_of_win':160},
        {'date':'2014-05-27', 'time_of_win': '14:26', 'win_number':2, 'renchan':0, 'spin_count_of_win':220},
        {'date':'2014-05-27', 'time_of_win': '14:35', 'win_number':3, 'renchan':1, 'spin_count_of_win':102},
        {'date':'2014-05-27', 'time_of_win': '14:46', 'win_number':4, 'renchan':0, 'spin_count_of_win':927},
        {'date':'2014-05-27', 'time_of_win': 'NaN', 'win_number':'--', 'renchan':0, 'spin_count_of_win':411},
    ]

    desire_data = [
        {'date':'2014-05-27', 'time_of_win': '13:45', 'win_number':1, 'renchan':0, 'spin_count_of_win':160, 'cash':-9412, 'balls':-483, 'balls_won':1870, 'cashout':6676, 'cash_result':-2736},
        {'date':'2014-05-27', 'time_of_win': '14:26', 'win_number':2, 'renchan':0, 'spin_count_of_win':220, 'cash':-9412, 'balls':0, 'balls_won':1940, 'cashout':6926, 'cash_result':-2486},
        {'date':'2014-05-27', 'time_of_win': '14:35', 'win_number':3, 'renchan':1, 'spin_count_of_win':102, 'cash':-9412, 'balls':0, 'balls_won':3810, 'cashout':13602, 'cash_result':4190},
        {'date':'2014-05-27', 'time_of_win': '14:46', 'win_number':4, 'renchan':0, 'spin_count_of_win':927, 'cash':-48647, 'balls':-6725, 'balls_won':1870, 'cashout':6676, 'cash_result':-51383},
        {'date':'2014-05-27', 'time_of_win': 'NaN', 'win_number':'--', 'renchan':0, 'spin_count_of_win':411 , 'cash':-18294, 'balls':-4665, 'balls_won':0, 'cashout':0, 'cash_result':-76353},
    ]

    result = add_cash_payout(test_data)
    print result
    return result == desire_data


if __name__ == '__main__':
    print test_add_cash_payout()