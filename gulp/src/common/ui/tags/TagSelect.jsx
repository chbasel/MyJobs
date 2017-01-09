import React, {Component, PropTypes} from 'react';
import {Tag} from 'common/ui/tags/Tag';
import TextField from 'common/ui/TextField';
import {map, filter, find} from 'lodash-compat/collection';
import {assign} from 'lodash-compat/object';

/**
 * Selection control for tags.
 */
export default class TagSelect extends Component {
  constructor() {
    super();
    this.state = {
      selectDropped: false,
      keySelectedIndex: null,
      mouseInMenu: false,
      partial: null,
    };
  }

  setHighlight(tags, highlight) {
    const newState = assign({}, ...map(tags, t =>
      ({['highlight-' + t.value]: highlight})));
    this.setState(newState);
  }

  getHighlight(tagValue) {
    const key = 'highlight-' + tagValue;
    return this.state[key];
  }

  getAddButton() {
    const {onNew} = this.props;

    if (onNew) {
      return (
        <div className="col-xs-12 col-md-3">
          <div className="button" onClick={() => this.handleNewTag()}>Add New</div>
        </div>
      );
    }
  }

  openSelectMenu() {
    this.setState({selectDropped: true});
  }

  closeSelectMenu() {
    this.setState({
      partial: '',
      selectDropped: false,
    });
  }

  toggleSelectMenu() {
    this.setState({selectDropped: !this.state.selectDropped});
  }

  handleFilterChange(value) {
    if (value) {
      this.setState({partial: value});
    } else {
      this.setState({partial: null});
    }
  }

  handleNewTag() {
    if (!this.state.partial) {
      return;
    }
    const {onNew} = this.props;
    onNew(this.state.partial);
    this.setState({partial: null});
  }

  selectAll() {
    this.handleAdd(this.filteredAvailable());
    this.closeSelectMenu();
  }

  filteredAvailable() {
    const {available, selected} = this.props;
    const {partial} = this.state;

    return filter(available, at =>
      (!partial ||
       at.display.toUpperCase().indexOf(partial.toUpperCase()) !== -1) &&
      !find(selected, st => st.value === at.value));
  }

  handleAdd(tags) {
    const {onChoose} = this.props;
    this.setHighlight(tags, false);
    onChoose(tags);
  }

  handleRemove(tags) {
    const {onRemove} = this.props;
    this.setHighlight(tags, false);
    onRemove(tags);
  }

  handleBlur() {
    const {mouseInMenu} = this.state;
    if (!mouseInMenu) {
      this.closeSelectMenu();
    }
  }

  handleMouseState(value) {
    this.setState({mouseInMenu: value});
  }

  renderTag(tag, handleClick, remove) {
    const highlight = this.getHighlight(tag.value);
    return (
      <Tag
        key={tag.value}
        display={tag.display}
        hexColor={tag.hexColor}
        onClick={() => handleClick(tag)}
        onMouseEnter={() => this.setHighlight([tag], true)}
        onMouseLeave={() => this.setHighlight([tag], false)}
        onRemoveTag={remove ? () => remove(tag) : undefined}
        highlight={highlight}/>
    );
  }

  render() {
    const {selected, placeholder, searchPlaceholder, onNew} = this.props;
    const {selectDropped, partial} = this.state;
    const filteredAvailable = this.filteredAvailable();

    return (
      <div className="tag-select-input-element"
        tabIndex="0"
        onBlur={e => this.handleBlur(e)}
        onMouseEnter={() => this.handleMouseState(true)}
        onMouseLeave={() => this.handleMouseState(false)}>
        <div
          className="tag-select-chosen-tags"
          onClick={() => this.toggleSelectMenu()}>
          {(selected.length !== 0)
            ? ''
            : (
              <span className="tag-select-placeholder">
                {placeholder}
              </span>
              )}
          {map(selected, t => this.renderTag(
              t,
              () => {},
              () => this.handleRemove([t])))}
        </div>
        {selectDropped ? (
          <div className="tag-select-menu-container">
            <div className="tag-select-menu">
              <div className="container-fluid">
                <div className="row">
                  <div className={'col-xs-12 col-md-' + (onNew ? '6' : '8') }>
                    <TextField
                      name="name"
                      value={partial}
                      onChange={e => this.handleFilterChange(e.target.value)}
                      placeholder={searchPlaceholder} />
                  </div>
                  { this.getAddButton() }
                  <div className={'col-xs-12 col-md-' + (onNew ? '3' : '4' )}>
                    <div className="button" onClick={() => this.selectAll()}>Select All</div>
                  </div>
                </div>
                <div className="row">
                  {map(filteredAvailable, t => this.renderTag(
                      t,
                      () => this.handleAdd([t]),
                      null))}
                </div>
              </div>
            </div>
          </div>
        ) : '' }
      </div>
    );
  }
}

TagSelect.defaultProps = {
  available: [{value: '', display: '', hexColor: ''}],
  searchPlaceholder: 'Type to filter',
  placeholder: 'Not specified',
};

TagSelect.propTypes = {
  /**
   * List of selected tags.
   */
  selected: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
      hexColor: PropTypes.string,
    })
  ).isRequired,
  /**
   * List of available tags.
   */
  available: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
      hexColor: PropTypes.string,
    })
  ).isRequired,
  /**
   * Function called when available tags are selected.
   */
  onChoose: PropTypes.func.isRequired,
  /**
   * Function called when available tags are removed.
   */
  onRemove: PropTypes.func.isRequired,
  /**
   * placeholder text for tag search bar
   */
  searchPlaceholder: PropTypes.string,
  /**
   * placeholder text for select input
   */
  placeholder: PropTypes.any,

   /**
   *  function to handle adding a new tag, otherwise the "add new" button is
   *  hidden.
   */
  onNew: PropTypes.func,
};
