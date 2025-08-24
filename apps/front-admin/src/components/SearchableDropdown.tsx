import React, { useState, useRef, useEffect } from "react";
import "../resources/scss/components/dropdown_style.scss";
import { pointsService } from "../api/Points";

interface Point {
    id: number;
    RU_city: string;
    RU_country: string;
}

interface SearchableDropdownProps {
    placeholder?: string;
    value: Point | null;
    onSelect: (point: Point) => void;
    className?: string;
}

export const SearchableDropdown = ({
    placeholder = "Введите город",
    value,
    onSelect,
    className = "",
}: SearchableDropdownProps) => {
    const [ isOpen, setIsOpen ] = useState(false);
    const [ search, setSearch ] = useState("");
    const [ options, setOptions ] = useState<Point[]>([]);
    const [ displayValue, setDisplayValue ] = useState("");
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (value && value.RU_city && value.RU_country) {
            setDisplayValue(`${value.RU_country}, ${value.RU_city}`);
            setSearch(value.RU_city);
        } else {
            setDisplayValue("");
            setSearch("");
        }
    }, [ value ]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        const fetchPoints = async () => {
            if (!search.trim()) {
                setOptions([]);
                return;
            }

            try {
                const data = await pointsService.search(search);
                if (data.status === "OK") {
                    setOptions(data.point_name);
                }
            } catch (err) {
                console.error("Ошибка загрузки точек:", err);
                setOptions([]);
            }
        };

        const timeout = setTimeout(fetchPoints, 400);
        return () => clearTimeout(timeout);
    }, [ search ]);

    const handleSelect = (point: Point) => {
        onSelect(point);
        setDisplayValue(`${point.RU_country}, ${point.RU_city}`);
        setSearch(point.RU_city);
        setIsOpen(false);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setDisplayValue(newValue);
        setSearch(newValue);
        setIsOpen(true);

        if (newValue === "") {
            onSelect({ id: 0, RU_city: "", RU_country: "" });
            setOptions([]);
        }
    };

    const handleInputFocus = () => {
        setIsOpen(true);
        if (value && value.RU_city) {
            setDisplayValue(value.RU_city);
        }
    };

    const handleInputBlur = () => {
        if (value && value.RU_city && value.RU_country) {
            setDisplayValue(`${value.RU_country}, ${value.RU_city}`);
        }
    };

    return (
        <div className={ `dropdown-container ${className}` } ref={ dropdownRef }>
            <input
                type="text"
                className="dropdown-toggle"
                value={ displayValue }
                placeholder={ placeholder }
                onChange={ handleInputChange }
                onFocus={ handleInputFocus }
                onBlur={ handleInputBlur }
            />
            {isOpen && options.length > 0 && (
                <div className="dropdown-menu">
                    {options.map((point) => (
                        <div
                            key={ point.id }
                            className="dropdown-item"
                            onClick={ () => handleSelect(point) }
                        >
                            {point.RU_country}, {point.RU_city}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
