## Страницы
Страница - законченный элемент. Он использует виджеты (иногда - компоненты напрямую, но лучше этого избегать; допустимо только в очень простых случаях).
Страницы не могут использовать друг друга. Здесь не должно быть логики работы с данными, всю логику нужно максимально вынести в виджеты!

### Технология
Одна страница в одном TSX файле; `export default` всегда. Компоненты объявляются с суффиксом Page.

### Пример
```tsx
import MainLayout from "layouts/main";
import Header from "widgets/header";
import CommentsBlock from "widgets/comments-block";
import CommentForm from "widgets/comment-form";

export default function CommentPage() {
    return (
        <MainLayout>
            <Header title="Routes Calculator" />
            <main>
                <div>
                    <CommentsBlock />
                </div>
                <div>
                    <CommentForm />
                </div>
            </main>
        </MainLayout>
    );
}
```
