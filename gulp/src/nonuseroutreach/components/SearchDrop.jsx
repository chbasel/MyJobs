import React, {Component, PropTypes} from 'react';
import {map, contains} from 'lodash-compat/collection';
import {connect} from 'react-redux';
import {typingDebounce} from 'common/debounce';
import classnames from 'classnames';
import {SmoothScroller} from 'common/dom';
import {expandStaticUrl} from 'common/assets';

import {
  doSearch,
  searchUpdateAction,
  resetSearchOrAddAction,
  addToActiveIndexAction,
  setActiveIndexAction,
  searchResultSelectedAction,
} from 'nonuseroutreach/actions/search-or-add-actions';

export default class SearchDrop extends Component {
  constructor() {
    super();

    this.debouncedOnSearch = typingDebounce(() => {
      const {dispatch, instance, extraParams} = this.props;
      dispatch(doSearch(instance, extraParams));
    });
    this.liRefs = {};
    this.movedByKeyboard = false;
    this.mouseInControl = false;
  }

  componentDidMount() {
    this.scroller = new SmoothScroller(v => this.scrollTo(v));
  }

  componentDidUpdate(prevProps) {
    const {activeIndex: prevActiveIndex} = prevProps;
    const {activeIndex} = this.props;

    if (prevActiveIndex !== activeIndex) {
      if (this.movedByKeyboard) {
        this.movedByKeyboard = false;
        this.springToActiveLi();
      } else {
        if (this.container) {
          this.scroller.skipTo(this.container.scrollTop);
        }
      }
    }
  }

  componentWillUnmount() {
    this.scroller.destroy();
  }

  handleBlur() {
    if (!this.mouseInControl) {
      const {dispatch, instance} = this.props;
      dispatch(resetSearchOrAddAction(instance));
    }
  }

  handleSearchChange(e) {
    const {dispatch, instance} = this.props;
    const value = e.target.value;

    dispatch(searchUpdateAction(instance, value));
    this.debouncedOnSearch();
  }

  handleMouseOver(i) {
    const {dispatch, instance} = this.props;
    dispatch(setActiveIndexAction(instance, i));
  }

  handleSelect(forceAdd) {
    const {
      dispatch,
      instance,
      results,
      activeIndex,
      searchString,
      onSelect,
      onAdd,
    } = this.props;
    if (!forceAdd && results && results.length) {
      const result = results[activeIndex];
      dispatch(searchResultSelectedAction(instance, result));
      onSelect(result);
    } else if (onAdd) {
      const result = {value: '', display: searchString};
      dispatch(searchResultSelectedAction(instance, result));
      onAdd(result);
    }
  }

  handleLiRef(ref, i) {
    if (ref) {
      this.liRefs[i] = ref;
    } else {
      delete this.liRefs[i];
    }
  }

  handleCancel() {
    const {dispatch, instance} = this.props;
    dispatch(resetSearchOrAddAction(instance));
    this.input.focus();
  }

  springToActiveLi() {
    const {activeIndex} = this.props;
    if (!activeIndex && activeIndex !== 0) {
      return;
    }

    const ref = this.liRefs[activeIndex];
    this.scroller.springToShow(ref, this.container);
  }

  scrollTo(offset) {
    if (this.container) {
      this.container.scrollTop = offset;
    }
  }

  filterKeys(e) {
    const {dispatch, instance} = this.props;

    if (e.key === 'Enter') {
      e.preventDefault();
      this.handleSelect();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      dispatch(resetSearchOrAddAction(instance));
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      this.movedByKeyboard = true;
      dispatch(addToActiveIndexAction(instance, 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this.movedByKeyboard = true;
      dispatch(addToActiveIndexAction(instance, -1));
    }
  }

  renderResults() {
    const {results, searchString, activeIndex} = this.props;

    if (results.length) {
      return (
        <ul>
          {map(results, (result, i) => (
            <li
              key={i}
              ref={ref => this.handleLiRef(ref, i)}
              onMouseEnter={() => this.handleMouseOver(i)}
              onClick={() => this.handleSelect()}
              className={classnames(
                  {'active': i === activeIndex, 'list-result': true})}>
              {typeof result.count !== 'undefined' ?
                <span className="partner-count">({result.count} contact{result.count === 1 ? '' : 's'})</span>
                : ''}

              {result.display}

              {result.partner ?
                <span className="partner-count">({result.partner.name})</span>
                : ''}
            </li>
          ))}
        </ul>
      );
    }

    return `No results found for "${searchString}".`;
  }

  renderDropWrap(inner) {
    return (
      <div
        className="select-element-menu-container"
        ref={r => {this.container = r;}}
        >
        {inner}
      </div>
    );
  }

  renderDrop() {
    const {
      state,
      searchString,
      results,
      onAdd,
    } = this.props;

    if (state === 'PRELOADING' || state === 'LOADING') {
      return this.renderDropWrap(
        <div className="search-drop-empty"></div>
      );
    } else if (state === 'RECEIVED' && results.length) {
      return this.renderDropWrap(this.renderResults());
    } else if (state === 'RECEIVED') {
      return this.renderDropWrap(
        <div className="search-drop-action">
          <p>{searchString}</p>
          <p>was not found in our database</p>
          {onAdd ?
            <div className="search-drop-controls">
              <button
                onClick={() => this.handleCancel()}
                className="btn">
                Cancel
              </button>
              <button
                onClick={() => this.handleSelect()}
                className="btn primary">
                Create
              </button>
            </div>
          : ''}
        </div>
      );
    }
    return '';
  }

  renderTrayIcon(key, children) {
    return (
      <div
        key={key}
        className="tray-item">
        {children}
      </div>
    );
  }

  renderLoadingIcon() {
    const {state} = this.props;

    if (contains(['SELECTED', 'LOADING'], state)) {
      return (
        <img
          alt="[loading]"
          src={expandStaticUrl('images/ajax-loader.gif')}/>
      );
    }

    return null;
  }

  renderCreateIcon() {
    const {state, onAdd} = this.props;

    if (state === 'RECEIVED' && onAdd) {
      return (
        <img
          alt="[create]"
          src={expandStaticUrl('svg/arrow-right.svg')}
          onClick={() => this.handleSelect(true)}
          />
      );
    }

    return null;
  }

  renderTrayItems() {
    const items = [
      this.renderTrayIcon('loading', this.renderLoadingIcon()),
      this.renderTrayIcon('create', this.renderCreateIcon()),
    ];

    return (
      <div className="tray-items">
        {items}
      </div>
    );
  }

  renderInput() {
    const {searchString, state, selected} = this.props;

    if (state === 'SELECTED') {
      return (
        <input
          className="search-or-add-loading-icon"
          value={selected.display}/>
      );
    }

    return (
      <input
        ref={r => this.input = r}
        onBlur={() => this.handleBlur()}
        onKeyDown={e => this.filterKeys(e)}
        type="search"
        value={searchString}
        onChange={e => this.handleSearchChange(e)}
        />
    );
  }

  render() {
    return (
      <div
        className="dropdown"
        onMouseEnter={() => {this.mouseInControl = true;}}
        onMouseLeave={() => {this.mouseInControl = false;}}>
        <div className="tray-container">
          {this.renderTrayItems()}
          <div className="tray-content">
            {this.renderInput()}
          </div>
        </div>
        {this.renderDrop()}
      </div>
    );
  }
}

SearchDrop.defaultProps = {
  searchString: '',
  extraParams: {},
};

SearchDrop.propTypes = {
  dispatch: PropTypes.func.isRequired,
  instance: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  searchString: PropTypes.string.isRequired,
  results: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    })),
  selected: PropTypes.shape({
    value: PropTypes.any.isRequired,
    display: PropTypes.string.isRequired,
  }),
  activeIndex: PropTypes.number,
  extraParams: PropTypes.object,
  onAdd: PropTypes.func,
  onSelect: PropTypes.func.isRequired,
};

export default connect((state, ownProps) => ({
  state: state.search[ownProps.instance].state,
  searchString: state.search[ownProps.instance].searchString,
  results: state.search[ownProps.instance].results,
  selected: state.search[ownProps.instance].selected,
  activeIndex: state.search[ownProps.instance].activeIndex,
}))(SearchDrop);
