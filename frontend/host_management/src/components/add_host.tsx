import React, {Component} from 'react'
import Modal from 'react-modal';

export default class extends Component<any, any> {
    constructor(props) {
        super(props);
        this.state = {
            modal: false,
            link: ''
        }
    }

    render() {
        const {modal, link} = this.state;
        const {add_host} = this.props;
        return (
            <div>
                <div>
                    <button
                        className="group relative flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        onClick={() => this.setState({modal: true, link: add_host})}
                    >
                        Add Host
                    </button>
                </div>
                <Modal
                    isOpen={modal}
                    onRequestClose={() => this.setState({modal: false})}
                    style={{
                        content: {
                            display: 'flex',
                            flexDirection: 'column'
                        }
                    }}
                    contentLabel="Modal"
                >
                    <button className="modal-close cursor-pointer z-50 ml-auto"
                            onClick={() => this.setState({modal: false})}>
                        <svg className="fill-current text-black" xmlns="http://www.w3.org/2000/svg" width="18"
                             height="18" viewBox="0 0 18 18">
                            <path
                                d="M14.53 4.53l-1.06-1.06L9 7.94 4.53 3.47 3.47 4.53 7.94 9l-4.47 4.47 1.06 1.06L9 10.06l4.47 4.47 1.06-1.06L10.06 9z"></path>
                        </svg>
                    </button>
                    <iframe src={link} className="w-full h-full"/>
                </Modal>
            </div>
        )
    }
}
