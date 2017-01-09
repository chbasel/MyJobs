import React from 'react';
import {Component} from 'react';

class DimensionList extends Component {
  constructor() {
    super();
    this.state = {
      activeList: false,
    };
  }
  toggleDimensionList() {
    this.setState({
      activeList: !this.state.activeList,
    });
  }
 render() {
   return (
     <div onClick={this.toggleDimensionList.bind(this)} className={this.state.activeList ? 'dimension_list open' : 'dimension_list'}>
       <span className={this.state.activeList ? 'dimension-title exit' : 'dimension-title'}>
         <span className="add-dimension">Add Dimension</span>
         <span className="dimension-icon"></span>
         <span className="dimension-icon"></span>
       </span>
       <ul className="list">
       <li><a href="#">Dimension 1</a></li>
         <li><a href="#">Dimension 2</a></li>
         <li><a href="#">Dimension 3</a></li>
         <li><a href="#">Dimension 4</a></li>
        <li><a href="#">Dimension 5</a></li>
       </ul>
     </div>
   );
 }
}

export default DimensionList;
