from models import *

session = Session()

user_1 = User(username='m2', first_name='Jake', last_name='Kikman', email='jakkik@gmail.com',
              password='11111', phone='380558695222', user_status=0)
user_2 = User(username='softserve', first_name='Vanda', last_name='Maksimova', email='vanmak@gmail.com',
              password='12345', phone='380962358712', user_status=1)
article_1 = Article(name='IT news', text='Google is searching for ways to reassure people that it is still '
                                         'out in front in the race for the best artificial intelligence technology. '
                                         'And so far, the internet giant seems to be coming up with the wrong answer. '
                                         'An advert designed to show off its new AI bot, showed it answering a query '
                                         'incorrectly.',
                    articleCreator=user_1, version=0)
article_2 = Article(name='Kitties', text='A kitten is a juvenile cat. After being born, kittens display primary '
                                         'altriciality and are totally dependent on their mothers for survival. They '
                                         'normally do not open their eyes for seven to ten days. After about two weeks,'
                                         'kittens develop quickly and begin to explore the world outside their nest. '
                                         'After a further three to four weeks, they begin to eat solid food and grow '
                                         'baby teeth. Domestic kittens are highly social animals and usually enjoy '
                                         'human companionship.',
                    articleCreator=user_2, version=0)
change_1 = Change(articleChanged=article_1, new_text='Kitten, ha-ha-ha-ha', changeProposer=user_2,
                  article_version=article_1.version, old_text=article_1.text)
change_2 = Change(articleChanged=article_2, new_text='Bad, broken news', changeProposer=user_1,
                  article_version=article_2.version, old_text=article_2.text)
review_1 = Review(changeReviewed=change_1, verdict=0, comment='Stop joking', reviewer=user_1)
review_2 = Review(changeReviewed=change_2, verdict=0, comment='Please, don`t ruin my articles', reviewer=user_2)
#
session.add_all([user_1, user_2, article_1, article_2, change_1, change_2, review_1, review_2])

session.commit()
