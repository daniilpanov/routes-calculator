## Страницы
Страница - законченный элемент. Он использует виджеты (иногда - компоненты напрямую, но лучше этого избегать; допустимо только в очень простых случаях).
Страницы не могут использовать друг друга. Здесь не должно быть логики работы с данными, всю логику нужно максимально вынести в виджеты!

### Технология
Одна страница в одном TSX файле; `export default` всегда.

### Пример
```tsx
import CommentsBlock from "widgets/comments-block";
import CommentForm from "widgets/comment-form";

export default function Comment() {
    return (
        <main>
            <div>
                <CommentsBlock />
            </div>
            <div>
                <CommentForm />
            </div>
        </main>
    );
}
```
