import React from 'react';

/**
 * Simple input element with onChange handler
 */
function TextField(props) {
  const {
    name,
    onChange,
    required,
    maxLength,
    value,
    isHidden,
    placeholder,
    autoFocus,
    onFocus,
    className,
    onBlur,
    disable,
  } = props;

  return (
    <span className="react-component">
      <input
        type="text"
        autoComplete="off"
        id={name}
        name={name}
        className={className}
        maxLength={maxLength}
        required={required}
        hidden={isHidden}
        value={value}
        placeholder={placeholder}
        onChange={onChange}
        autoFocus={autoFocus}
        onFocus={onFocus}
        disabled={disable}
        onBlur={onBlur}
        />
    </span>
  );
}

TextField.propTypes = {
  /**
  * Callback: the user edited this field
  *
  * obj: change event
  */
  onChange: React.PropTypes.func.isRequired,
  /**
   * under_score_seperated, unique name of this field. Used to post form
   * content to Django
   */
  name: React.PropTypes.string.isRequired,
  /**
   * Placeholder text for the input control
   */
  placeholder: React.PropTypes.string,
  /**
   * Value shown in control
   */
  value: React.PropTypes.string,
  /**
   * Number of characters allowed in this field
   */
  maxLength: React.PropTypes.number,
  /**
   * Should this component be shown or not?
   */
  isHidden: React.PropTypes.bool,
  /**
   * Must this field have a value before submitting form?
   */
  required: React.PropTypes.bool,
  /**
   * Should this bad boy focus, all auto like?
   */
  autoFocus: React.PropTypes.string,
  /**
   * What happens if you click this field?
   */
  onFocus: React.PropTypes.func,
  /**
   * What happens onBlur?
   */
  onBlur: React.PropTypes.func,
  /**
   * Disable this control
   */
  disable: React.PropTypes.bool,
  /**
   * Classes
   */
  className: React.PropTypes.string,
};

TextField.defaultProps = {
  placeholder: '',
  value: '',
  maxLength: null,
  isHidden: false,
  required: false,
  autoFocus: '',
  onFocus: null,
  onBlur: null,
  className: '',
};

export default TextField;
