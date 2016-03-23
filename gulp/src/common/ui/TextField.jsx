import React from 'react';

function TextField(props) {
  const {name, onChange, required, maxLength, initial, isHidden, placeholder} = props;
  return (
    <input
      type="text"
      id={name}
      name={name}
      className=""
      maxLength={maxLength}
      required={required}
      hidden={isHidden}
      defaultValue={initial}
      placeholder={placeholder}
      onChange={onChange}
      />
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
   * Value at first page load
   */
  initial: React.PropTypes.string,
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
};

TextField.defaultProps = {
  placeholder: '',
  initial: '',
  maxLength: null,
  isHidden: false,
  required: false,
};

export default TextField;
