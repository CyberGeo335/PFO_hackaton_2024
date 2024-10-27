if (!localStorage['question']) {
    localStorage['question'] = 0;
}



class LocalStorage {

    static GetQuestionType() {
        return localStorage['question'];
    }

    static SetQuestionType(type) {
        localStorage['question'] = type;
    }
}

export { LocalStorage }