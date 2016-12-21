import React from 'react';
import classnames from 'classnames';

/**
 * Custom select box (i.e. not standard HTML form element) with keyboard support
 */
class Select extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectDropped: false,
      keySelectedIndex: null,
    };
    this.openSelectMenu = this.openSelectMenu.bind(this);
    this.closeSelectMenu = this.closeSelectMenu.bind(this);
  }
  onInputKeyDown(event) {
    const {choices, name} = this.props;
    const {keySelectedIndex, selectDropped} = this.state;

    let killEvent = false;

    if (selectDropped && event.key === 'ArrowDown') {
      killEvent = true;
      this.shiftKeySelectedIndex(1);
    } else if (selectDropped && event.key === 'ArrowUp') {
      killEvent = true;
      this.shiftKeySelectedIndex(-1);
    } else if (selectDropped && event.key === 'Enter') {
      killEvent = true;
      this.selectFromMenu(choices[keySelectedIndex], name);
    } else if (selectDropped && event.key === 'Escape') {
      killEvent = true;
      this.closeSelectMenu();
    } else if (event.key === 'ArrowDown') {
      killEvent = true;
      this.resetKeySelectedIndex();
      this.openSelectMenu();
    }
    if (killEvent) {
      event.preventDefault();
      event.stopPropagation();
    }
  }
  onMenuItemEnter(index) {
    this.setState({keySelectedIndex: index});
  }
  onMouseEnter() {
    this.preventClose = true;
  }
  onMouseLeave() {
    this.preventClose = false;
  }
  shiftKeySelectedIndex(delta) {
    const {choices} = this.props;
    const {keySelectedIndex} = this.state;
    const lastIndex = choices.length - 1;

    let newIndex = keySelectedIndex + delta;

    if (newIndex < 0) {
      newIndex = lastIndex;
    }
    if (newIndex > lastIndex) {
      newIndex = 0;
    }
    this.setState({keySelectedIndex: newIndex});
  }
  resetKeySelectedIndex() {
    this.setState({keySelectedIndex: 0});
  }
  openSelectMenu() {
    this.setState({selectDropped: true});
  }
  closeSelectMenu() {
    if (!this.preventClose) {
      this.setState({selectDropped: false});
    }
  }
  selectFromMenu(itemKey, name) {
    const {onChange} = this.props;
    // With an HTML select we can use an onChange handler and we get a nice event
    // object. Here we have to fake it.
    const fakeEvent = {};
    fakeEvent.target = {};
    fakeEvent.target.name = name;
    fakeEvent.target.type = 'advanced-select';
    fakeEvent.target.value = itemKey.value;
    fakeEvent.target.obj = itemKey;

    onChange(fakeEvent);

    this.preventClose = false;
    this.closeSelectMenu();
  }
  render() {
    const {choices, name, value, disable} = this.props;
    const {keySelectedIndex, selectDropped} = this.state;

    let selectAction;
    let dropdown;
    let dropdownItems = [];
    if (selectDropped) {
      if (disable === true) {
        selectAction = null;
      } else {
        selectAction = this.closeSelectMenu;
      }
      dropdownItems = choices.map((item, index)=> {
        let active = '';
        if (index === keySelectedIndex) {
          active = 'active';
        }
        return (
          <li
            key={index}
            className={active}
            onMouseEnter={() => this.onMenuItemEnter(index)}
            onClick={() => this.selectFromMenu(item, name)}>
              {item.display}
            </li>
          );
      });

      dropdown = (
      <div
        className="select-element-menu-container"
        onMouseEnter={() => this.onMouseEnter()}
        onMouseLeave={() => this.onMouseLeave()}>
        <ul>
          {dropdownItems}
        </ul>
      </div>
      );
    } else {
      if (disable === true) {
        selectAction = null;
      } else {
        selectAction = this.openSelectMenu;
      }
      dropdown = '';
    }

    return (
      <div className="select-element-outer" tabIndex="0" onBlur={this.closeSelectMenu} onKeyDown={e => this.onInputKeyDown(e)}>
        <div className={
          classnames(
            'select-element-input',
            {'disabled': disable})}
          onClick={selectAction}>
          <div className="select-element-chosen-container">
            <span className="select-element-chosen">{value}</span>
            <span className="select-element-arrow">
              <b role="presentation"></b>
            </span>
          </div>
        </div>
        {dropdown}
      </div>
    );
  }
}

Select.defaultProps = {
  value: '',
};

Select.propTypes = {
  /**
  * Callback: the user has selected an item.
  *
  * obj: the object selected by the user.
  */
  onChange: React.PropTypes.func.isRequired,
  /**
   * under_score_seperated, unique name of this field. Used to post form
   * content to Django
   */
  name: React.PropTypes.string.isRequired,
  /**
   * Value shown as the selected value in the control.
   */
  value: React.PropTypes.oneOfType([
    React.PropTypes.string,
    React.PropTypes.element,
  ]),
  /**
   * Array of objects, each an item in the select component
   */
  choices: React.PropTypes.arrayOf(
    React.PropTypes.shape({
      value: React.PropTypes.any.isRequired,
      display: React.PropTypes.string.isRequired,
    })
  ),
  /**
   * Array of strings, each a possible error produced by Django
   */
  errors: React.PropTypes.arrayOf(React.PropTypes.string),
  /**
   * Ability to disable the select control
   */
  disable: React.PropTypes.bool,
};

export default Select;
