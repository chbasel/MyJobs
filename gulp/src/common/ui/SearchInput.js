import React, {Component, PropTypes} from 'react';
import classnames from 'classnames';


/**
 * Dropdown search box which empties itself after selecting an item.
 */
export class SearchInput extends Component {
  constructor(props) {
    super();
    const {value} = props;
    this.state = this.getDefaultState(value);
  }

  handleInputChange(event) {
    const value = event.target.value;
    this.setState({value});
    if (value) {
      this.search(value);
    } else {
      this.clear('');
    }
  }

  handleInputBlur() {
    const {value, mouseInMenu} = this.state;
    // When the user clicks a menu item, this blur event fires before the click
    // event in the dropdown menu. Our usual handling of blur makes handling the
    // click impossible. Avoid our usual blur handling if the pointer is in the
    // dropdown menu.
    if (mouseInMenu) {
      this.focus();
    } else {
      const {onBlur, callSelectWhenEmpty, onSelect} = this.props;
      if (callSelectWhenEmpty && value === '') {
        onSelect('');
      }
      onBlur();
      this.clear(value);
    }
  }

  handleMouseInMenu(value) {
    this.setState({mouseInMenu: value});
  }

  handleSelect(e, index) {
    e.preventDefault();
    const {hints, onSelect} = this.props;
    const selected = hints[index];
    onSelect(selected);
    const {emptyOnSelect} = this.props;
    if (emptyOnSelect) {
      this.clear('');
    } else {
      this.clear(selected.display);
    }
  }

  handleInputKeyDown(event) {
    const {hints} = this.props;
    const {keySelectedIndex, value} = this.state;
    if (hints && hints.length) {
      let newIndex = keySelectedIndex;
      let killEvent = false;
      const lastIndex = hints.length - 1;
      if (event.key === 'ArrowDown') {
        killEvent = true;
        if (keySelectedIndex < 0 || keySelectedIndex >= lastIndex) {
          newIndex = 0;
        } else {
          newIndex += 1;
        }
      } else if (event.key === 'ArrowUp') {
        killEvent = true;
        if (keySelectedIndex <= 0 || keySelectedIndex > lastIndex) {
          newIndex = lastIndex;
        } else {
          newIndex -= 1;
        }
      } else if (event.key === 'Enter') {
        killEvent = true;
        if (keySelectedIndex >= 0 && keySelectedIndex <= lastIndex) {
          this.handleSelect(event, keySelectedIndex);
          return;
        }
      } else if (event.key === 'Escape') {
        killEvent = true;
        this.clear(value);
      }
      if (killEvent) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.setState({keySelectedIndex: newIndex});
    }
  }

  getDefaultState(value) {
    return {
      value,
      mouseInMenu: false,
      keySelectedIndex: -1,
      dropped: false,
    };
  }

  async search(value) {
    const {getHints} = this.props;
    this.setState({dropped: true});
    await getHints(value);
  }

  focus() {
    const {input} = this.refs;
    input.focus();
  }

  clear(newValue) {
    this.setState(this.getDefaultState(newValue));
  }

  suggestId() {
    const {id} = this.props;
    return id + '-suggestions';
  }

  itemId(index) {
    const id = this.suggestId();
    if (index <= 0) {
      return null;
    }
    return this.suggestId(id) + '-' + index.toString();
  }

  render() {
    const {id, theme, placeholder, autofocus, hints} = this.props;
    const {dropped, value, keySelectedIndex} = this.state;
    const suggestId = id + '-suggestions';

    const showItems = Boolean(dropped && hints && hints.length);
    const activeId = this.itemId(keySelectedIndex);

    return (
      <div
        className={classnames(
          theme.root,
          {[theme.rootOpen]: hints})}>
        <input
          className={theme.input}
          ref="input"
          placeholder={placeholder}
          onChange={e => this.handleInputChange(e)}
          onBlur={e => this.handleInputBlur(e)}
          onKeyDown={e => this.handleInputKeyDown(e)}
          value={value}
          type="search"
          aria-autocomplete="list"
          aria-owns={suggestId}
          aria-expanded={showItems}
          aria-activedescendant={activeId}
          autoFocus={autofocus} />
        {showItems ?
          <ul
            id={this.suggestId()}
            className={theme.suggestions}
            onMouseEnter={() => this.handleMouseInMenu(true)}
            onMouseLeave={() => this.handleMouseInMenu(false)}>
            {hints.map((hint, index) =>
              <li
                id={this.itemId(index)}
                key={hint.value}
                className={classnames(
                  theme.hint,
                  {
                    [theme.itemActive]: index === keySelectedIndex,
                  })}>
                <a
                  href="#"
                  onClick={e => this.handleSelect(e, index)}>
                  {hint.display}
                </a>
              </li>
            )}
          </ul>
        : null}
      </div>
    );
  }
}

SearchInput.defaultProps = {
  onBlur: () => {},
  emptyOnSelect: false,
  callSelectWhenEmpty: false,
  theme: {
    root: 'dropdown',
    rootOpen: 'open',
    input: '',
    suggestions: 'select-element-menu-container',
    item: '',
    itemActive: 'active',
  },
};

SearchInput.propTypes = {
  /**
   * Id for the input control. Must be unique within the page.
   *
   * Intended to support wai-aria.
   */
  id: React.PropTypes.string.isRequired,

  /**
   * Callback: the user has selected an item.
   *
   * obj: the object selected by the user.
   */
  onSelect: React.PropTypes.func.isRequired,

  /**
   * Empty input contents after selecting an item.
   */
  emptyOnSelect: React.PropTypes.bool,

  /**
   * If the select field is empty, call onSelect anyway.
   */
  callSelectWhenEmpty: React.PropTypes.bool,

  /**
   * Placeholder text for the input control
   */
  placeholder: React.PropTypes.string,

  /**
   * Callback: the user has changed the input. Need hints.
   *
   * input: string with user input so far
   */
  getHints: React.PropTypes.func.isRequired,

  /**
   * What to show in the dropdown.
   *
   * [ {value: some id, display: "Display Value"} ]
   */
  hints: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    }).isRequired),

  /**
   * Callback: the user has left the search input.
   */
  onBlur: React.PropTypes.func,

  /**
   * Value for this control.
   */
  value: PropTypes.string.isRequired,

  /**
   * classes for various components
   *
   * root: Applied to the div containing the input and suggestions.
   * rootOpen: Applied to the root when open in addition to classes on root.
   * input: Applied to the input.
   * suggestions: Applied to the ul containing the suggestions.
   * item: Applied to the li containing a single suggestions.
   * itemActive: Applied to li selected via keyboard. (hover is used for mouse)
   */
  theme: React.PropTypes.object,
  /**
   * Should this bad boy focus, all auto like?
   */
  autofocus: React.PropTypes.string,
};
