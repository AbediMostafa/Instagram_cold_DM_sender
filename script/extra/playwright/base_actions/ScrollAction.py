from script.extra.playwright.base_actions.BaseAction import BaseAction
import random


class ScrollAction(BaseAction):

    def start(self, element=None, min_length=100, max_length=300, min_pause=2000, max_pause=4000):
        # Randomly generate scroll length if element is provided
        scroll_length = random.randint(min_length, max_length)

        # If element is provided, scroll that specific element; otherwise, scroll the entire page
        if element:
            self.ig.page.evaluate('''
                ({selector, scrollLength}) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        element.scrollBy({
                            top: scrollLength,
                            behavior: 'smooth'
                        });
                    }
                }
            ''', {'selector': element, 'scrollLength': scroll_length})
        else:
            self.ig.page.evaluate('''
                ({scrollLength}) => {
                    window.scrollBy({
                        top: scrollLength,
                        behavior: 'smooth'
                    });
                }
            ''', {'scrollLength': scroll_length})

        # Pause for the specified duration
        self.ig.pause(min_pause, max_pause)

