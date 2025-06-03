import { useState, useRef, useEffect } from "react";
import "./CitySelector.css";

export default function CitySelector({
  options,
  value,
  onChange,
  disabled = false,
  placeholder = "請選擇",
}: {
  options: string[];
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="city-selector" ref={ref}>
      <button
        type="button"
        className={`city-selector-button ${disabled ? "disabled" : ""}`}
        onClick={() => {
          if (!disabled) setOpen(!open);
        }}
        disabled={disabled}
      >
        {value || placeholder}
      </button>
      {open && !disabled && (
        <div className="city-selector-dropdown">
          {options.map((city) => (
            <button
              key={city}
              className={`city-option ${city === value ? "selected" : ""}`}
              onClick={() => {
                onChange(city);
                setOpen(false);
              }}
            >
              {city}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
