import React from "react";

interface IFormSubmitProps {
    children: React.ReactNode;
    type?: "button" | "submit" | "reset";
    className?: string;
    disabled?: boolean
    onclick?: () => void;
}

export default function FormSubmit({ children, type = "submit", className, disabled, onclick }: IFormSubmitProps) {
    return (
        <button type={ type } className={ className } disabled={ disabled } onClick={ onclick }>
            { children }
        </button>
    );
}
