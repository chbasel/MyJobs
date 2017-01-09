import React, {PropTypes, Component} from 'react';
import {SearchInput} from 'common/ui/SearchInput';


export default class FilterSearchDropdown extends Component {
  onSearchSelect(value) {
    const {updateFilter} = this.props;
    updateFilter(value.value);
  }

  render() {
    const {id, placeholder, value, getHints, hints, loading} = this.props;
    const eid = 'filter-autosuggest-' + id;

    return (
      <SearchInput
        id={eid}
        value={value}
        callSelectWhenEmpty
        placeholder={placeholder}
        onSelect={v => this.onSearchSelect(v)}
        hints={hints}
        loading={loading}
        getHints={p => getHints(p)}/>
    );
  }
}

FilterSearchDropdown.propTypes = {
  id: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  updateFilter: PropTypes.func.isRequired,
  getHints: PropTypes.func.isRequired,
  hints: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    }).isRequired),
  placeholder: PropTypes.string,
  loading: PropTypes.bool,
};
