import { Component } from "react";
import './styles/MainPage.css'
import { QuestionDropDown } from "./QuestionDropDown";
import { LocalStorage } from "./LocalStorage";


class MainPage extends Component {

    constructor() {
        super();
        this.state = {
            questionQuery: "",
            summaryQuery: "",
            files: [],
            attachStatus: parseInt(LocalStorage.GetQuestionType()) === 1,
            summaryStatus: false,
        }
        this.openDropDown = this.openDropDown.bind(this);
        this.statusChange = this.statusChange.bind(this);
        this.sendSummaryQuery = this.sendSummaryQuery.bind(this);
        this.sendDatabaseQuery = this.sendDatabaseQuery.bind(this);
        this.sendQuestionQuery = this.sendQuestionQuery.bind(this);
    }

    openDropDown() {
        const drop = document.getElementById("drop-down")
        drop.style.display = 'flex'
        drop.classList.add("clicked")
    }

    fileOnChange(e) {
        const files = e.target.files;
        this.setState({ files: Array.from(files)});
        this.setState({summaryStatus:true})
        this.state.files.map((item, index) => console.log(item.name))
    }

    questionQueryOnChange(e) {
        this.setState({questionQuery: e.target.value})
    }

    statusChange() {
        this.setState({attachStatus: !this.state.attachStatus });
    }

    sendSummaryQuery() {
        console.log({"query": "суммаризация" })
    }

    sendDatabaseQuery() {
        console.log({"query": "база знаний:" + this.state.questionQuery})
    }

    sendQuestionQuery() {
        const formData = new FormData();
        this.state.files.map((item, index) => formData.append("file" + index, item))
        console.log({"query": this.state.questionQuery, formData})
    }

    render() {
        return(
            <div className="main-page-container">
                <div className="left-container"></div>
                <div className="main-content-container">
                    <div className="info-container">
                        <div className="team-tag">GreenQuery</div>
                        <div className="pfo-info">
                            <img className="rotate-img" src={require('./icons/rotate.png')} alt="Крутилка"></img>
                            <div onClick={this.openDropDown} className="question-info">
                                <img src={require('./icons/question-white.png')} width={20} height={20} alt="Задать вопрос"></img>
                                <div>Задать вопрос</div>
                            </div>
                            <QuestionDropDown id="drop-down" changeStatus={this.statusChange} ></QuestionDropDown>
                            <div className="summary-info" style={!this.state.summaryStatus ? {opacity: '0.5', pointerEvents: 'none'} : {opacity: '1', pointerEvents: 'all'}} onClick={this.sendSummaryQuery}>
                                <img src={require('./icons/summary-white.png')} width={20} height={20} alt="Суммаризация/QnA"></img>
                                <div>Суммаризация</div>
                            </div>
                            <div style={!this.state.attachStatus ? {opacity: '0.5', pointerEvents: 'none'}: {opacity: '1', pointerEvents: 'all'}} className="attach-file-info">
                                <div style={{position: 'relative', display: 'flex', flexDirection: 'row', gap: '5px'}}>
                                    <img src={require('./icons/attach-white.png')} width={20} height={20} alt="Прикрепить файл"></img>
                                    <div>Прикрепить файл</div>
                                    <input style={!this.state.attachStatus ? {pointerEvents: 'none'}: {pointerEvents: 'all'}} className="attach-file" id="files" name="files" multiple accept=".docx, .pdf" type="file" onChange={e => this.fileOnChange(e)}></input>
                                    
                                </div>
                                <div className="file-container">
                                    <div className="file-text">
                                    {this.state.files.map((item, index) => (
                                         <div key={index}>{item.name}</div>
                                ))} 
                                    </div>
                                </div>        
                            </div>
                            
                        </div>
                    </div> 
                    <div className="responce-container">
                        <div className="responce-text"></div>
                    </div>
                    <div className="inputs-container">
                        <div className="question-input-container">
                            <input className="question-input" type="text" placeholder="Какой вопрос вы бы хотели задать?" onChange={(e) => this.questionQueryOnChange(e)}></input>
                            <img className="send-img" src={require('./icons/send-white.png')} width={25} height={25} alt="Послать" onClick={parseInt(LocalStorage.GetQuestionType()) === 0 ? this.sendDatabaseQuery : this.sendQuestionQuery}></img>
                        </div>
                    </div>   
                </div>
                <div className="right-container"></div>
            </div>     
        )
    }
}

export {MainPage}