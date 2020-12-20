import React, {Component} from 'react'
import {render} from 'react-dom'

import Example from '../../src'

export default class Demo extends Component {
  render() {
    return <div>
      <h1>host_management Demo</h1>
      <Example.AddHost hosts={[{hostname: 'dlbeast'}]}/>
    </div>
  }
}

render(<Demo/>, document.querySelector('#demo'))
