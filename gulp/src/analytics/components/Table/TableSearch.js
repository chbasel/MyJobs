import React from 'react';
import {Component} from 'react';

class TableSearch extends Component {
  render() {
    const {searchData} = this.props;
    return (
      <input type="text" id={'search_table_tab_' + searchData.navId} className="search-table" placeholder="Search..." title="Type Search" />
    );
  }
}

TableSearch.propTypes = {
  searchData: React.PropTypes.object.isRequired,
};

export default TableSearch;
