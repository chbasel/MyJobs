import React from 'react';
import {Component} from 'react';

class Table extends Component {
  render() {
    const {tableData} = this.props;
    return (
      <div id={'table_data_tab_' + tableData.navId} className="table-data">
        <div id={'table_search_tab_' + tableData.navId} className="table-search">
            </div>
            <div className="clearfix"></div>
        <table id={'data_table_tab_' + tableData.navId} className="title-data rwd-table">
          {this.props.children}
        </table>
      </div>
    );
  }
}

Table.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  tableData: React.PropTypes.object.isRequired,
};

export default Table;
