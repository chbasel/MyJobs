import React from 'react';

/**
 * Simple Textarea element with onChange handler
 */
function Textarea(props) {
  const {
    name,
    onChange,
    required,
    initial,
    isHidden,
    placeholder,
    autoFocus,
    disable,
  } = props;

  return (
    <textarea
      defaultValue={initial}
      id={name}
      name={name}
      required={required}
      hidden={isHidden}
      placeholder={placeholder}
      onChange={onChange}
      disabled={disable}
      autoFocus={autoFocus}
      />
  );
}

Textarea.propTypes = {
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
   * Value at first page load
   */
  initial: React.PropTypes.string,
  /**
   * Should this component be shown or not?
   */
  isHidden: React.PropTypes.bool,
  /**
   * Must this field have a value before submitting form?
   */
  required: React.PropTypes.bool,
  /**
   * Disable this control
   */
  disable: React.PropTypes.bool,
  /**
   * Should this bad boy focus, all auto like?
   */
  autoFocus: React.PropTypes.string,
};

Textarea.defaultProps = {
  placeholder: '',
  initial: '',
  isHidden: false,
  required: false,
  autoFocus: '',
};

export default Textarea;
