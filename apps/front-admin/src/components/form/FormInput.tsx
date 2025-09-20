import React from "react";

interface IFormInputProps {
    type: string;
    name: string;
    value?: string;
    placeholder?: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    required?: boolean;
    className?: string;
}

export default function FormInput({ type, name, value, placeholder, onChange, required = false, className }: IFormInputProps) {
    return (
        <input
            type={ type }
            name={ name }
            value={ value }
            placeholder={ placeholder }
            onChange={ onChange }
            required={ required }
            className={ className }
        />
    );
}
