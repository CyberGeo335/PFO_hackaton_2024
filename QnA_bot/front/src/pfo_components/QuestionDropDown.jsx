import { Component } from "react";
import './styles/QuestionDropDown.css'
import { LocalStorage } from "./LocalStorage";

class QuestionDropDown extends Component {

    constructor(props) {
        super(props);
        this.closeDropDown = this.closeDropDown.bind(this);
        this.setQuestionDatabase = this.setQuestionDatabase.bind(this);
        this.setQuestionFile = this.setQuestionFile.bind(this);
    }

    closeDropDown() {
        const drop = document.getElementById(this.props.id)
        drop.classList.remove("clicked")
    }

    setQuestionDatabase() {
        const before = LocalStorage.GetQuestionType()
        LocalStorage.SetQuestionType(0);
        if (before !== LocalStorage.GetQuestionType()) {
            this.props.changeStatus()
        }
        console.log(LocalStorage.GetQuestionType())
        this.closeDropDown()
    }

    setQuestionFile() {
        const before = LocalStorage.GetQuestionType()
        LocalStorage.SetQuestionType(1)
        if (before !== LocalStorage.GetQuestionType()) {
            this.props.changeStatus()
        }
        console.log(LocalStorage.GetQuestionType())
        this.closeDropDown()
        
    }
    
    render() {
        return(
                <div id={this.props.id} className="drop-down-menu-container">
                    <div className="drop-down-menu-relative">
                        <div onClick={this.setQuestionDatabase}>По базе знаний</div>
                        <div onClick={this.setQuestionFile}>По файлу</div>
                    </div>  
                </div>
        )
    }
}

export {QuestionDropDown}