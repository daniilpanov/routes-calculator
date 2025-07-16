## Виджеты
Виджеты являются узкоспециализированными. Они описывают отдельные элементы сайта.

### Технология
Виджеты - такие же компоненты, но специализированные. Это как обёртка над группой компонентов, позволяющая быстро использовать их для определённой цели.
Здесь прописывается логика взаимодействия с данными. Виджеты могут использовать друг друга.

Виджеты также создаются с использованием TSX. Они могут использовать как кастомные компоненты, так и обычные HTML5-тэги.
Если в виджете не должно быть много стилей, можно не выносить HTML-тэг в отдельный компонент. Создание компонентов должно упрощать разработку, а не усложнять её!

Виджеты создаются ТОЛЬКО с использованием `export default`. В одном файле один виджет!

### Примеры использования
Допустим, у нас на странице есть заголовок с картинкой, контент, комментарии, форма "оставить комментарий".
Как будет выглядеть реализация?

1. Создадим виджет `header.tsx`.
   В нём всего лишь будут содержаться тэги `h2` и `img`:
```tsx
import logo from "./logo.png"; // relative path to image

interface TitleProps {
    title: string;
}

export default function Header({ title }: TitleProps) {
    return (
        <div className="header">
            <h2>{ title }</h2>
            <img src={ logo }/>
        </div>
    );
}
```

2. Создадим виджет `comment.tsx`
```tsx
// Interface example.
import { CommentProps } from "interfaces/comment.widget"
import Avatar from "components/avatar";

export default function Comment({ author, avatar, text }: CommentProps) {
    // Use Avatar custom component.
    return (
        <div className="comment">
            <div className="comment-header">
                <Avatar params={ avatar } />
                <span className="comment-author">{ author }</span>
            </div>
            <div className="comment-text">
                { text }
            </div>
        </div>
    );
}
```

3. Создадим виджет-агрегатор для `Comment` - `comments-block.tsx`
```tsx
import { getAllComments } from "api/comments";
import Comment from "./comment";

export default function CommentsBlock() {
    const comments = getAllComments();
    return (
        <div>
            { comments.map(comment => {
                <Comment key={ comment.id } { ...props }/>
            }) }
        </div>
    );
}
```

4. Создадим виджет `comment-form.tsx`
```tsx
import Form from "components/form/form";
import { FormInputControl } from "components/form/inputs";
import { FormSubmit, FormRatio } from "components/form/buttons";

export default function CommentForm() {
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Sending logic.
    };

    return (
        <Form className="comment-form">
            <FormInputControl label="Введите свой отзыв" />
            <FormRatio label="Показать имя" />
            <FormSubmit label="Отправить форму" onClick={ handleSubmit } />
        </Form>
    );
}
```
