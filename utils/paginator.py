class Paginator:
    def __init__(self, items, items_per_page):
        self.items = items
        self.items_per_page = items_per_page
        self.current_page = 1

    def total_pages(self):
        """Возвращает общее количество страниц."""
        return (len(self.items) + self.items_per_page - 1) // self.items_per_page

    def has_next(self):
        """Проверяет, есть ли следующая страница."""
        return self.current_page < self.total_pages()

    def next(self):
        """Переходит на следующую страницу, если она существует."""
        if self.has_next():
            self.current_page += 1

    def has_previous(self):
        """Проверяет, есть ли предыдущая страница."""
        return self.current_page > 1

    def previous(self):
        """Возвращается на предыдущую страницу, если она существует."""
        if self.has_previous():
            self.current_page -= 1

    def get_current(self):
        """Возвращает элементы текущей страницы."""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return self.items[start_index:end_index]

    def reset(self):
        """Сбрасывает текущую страницу на первую."""
        self.current_page = 1

    def get_start_index(self):
        """Возвращает индекс первого элемента на текущей странице."""
        return (self.current_page - 1) * self.items_per_page

    def get_end_index(self):
        """Возвращает индекс последнего элемента на текущей странице."""
        return min(self.get_start_index() + self.items_per_page, len(self.items))

    def is_empty(self):
        """Проверяет, является ли список элементов пустым."""
        return len(self.items) == 0
