from flask import jsonify, request
from services.elasticsearch_driver import get_learning_objects_without_topic
from services.mongodb_driver import get_all_topic_names
from topic_identification.learning_object_classification import determine_learning_object_placements
from topic_identification.learning_object_clustering import generate_new_topics

def TopicPredictionController(app):

    topics = ['Adversarial Thinking', 'SCADA', ' Networking and network security in the cloud', 'Strategic Thinking', 'NICE Challenges', 'Authenticating passwords', 'Secure Design with focus on IoT', 'CSEC Essentials roadmap', 'Modules on principles, networks, software vulnerabilities, development and acq. of secure software', 'Security networking; Systems and tools in security, and Adv. Security concepts', 'IoT security and privacy', 'Cyber Ethics, Cyber Security I and II, Scripting for automation and security, Wireless system admin., Digital Forensics', 'Industrial Control Systems', 'SCADA  Concept Maps ', 'Concept Maps for 3 courses', 'Cybersecurity 1 & 2, Networks, Software, Privacy, Crypto', 'Risk Management', 'Privacy', 'Competency-based curriculum', 'Software Security and Secure Programming', 'Digital Forensics, Secure Coding and Ethical Pen-testing, Cybersecurity and Digital Ethics ', 'Cybersecurity Principles course and modules on risk, mobile risk, software testing, ICS, LTE, and HCI', ' Introducing Active Learning to Malware Analysis Curriculum', 'Secure Software Development, Secure Programming, Op Sys Hardware, Network Defense', 'Modules for learning side-channel attacks and defenses on smartphones', 'Modules and labs for stepping-stone intrusion detection techniques', 'Content development of Reverse Engineering, Software Exp. & Security, Malware Analysis; K12 Ed Content; CTF, Framework Design', 'Basic and advanced topics in IoT Forensics', 'Education on laws, regulations and policies', 'Multidisciplinary (economics, psychology, and cybersecurity) approach to evaluate human threats and design systems for the desired human-computer interactions', 'Infrastructure Service Admin and Security, Advanced Network Security, Penetration Testing and Audit, Cybersecurity for Industrial Control Systems', 'Wireless/mobile and cyber threats and vulnerabilities', 'Quantum Cryptography Laboratories', 'Reverse engineering of modern malware', 'Intro to Cyber Security and Cloud Security', 'Android application vulnerabilities and mitigation ', 'Blockchain and Cybersecurity', 'Principles of Cyber Operation and Cyber Operations Law and Policy', 'Secure Programming Concept Inventory', 'Cybersecurity Legal and Ethical Aspects / Adversarial Thinking - 1 week module using behavorial game theory', 'Labs for Cryptographic Engineering on Modern Systems', 'Visualization tools and labs, Cross-Site Scripting and Cross-site Request Forgery, DNS cache poisoning and pharming, Logic Flaw, Ad Fraud, IoT Botnet, Browser Extensions', 'Threats/vuln., risk mgmt, software reverse eng., cryptography', 'Prototype Curriculum Management System (CLARK)', 'Software Reverse Engineering']

    @app.route('/topics/assign', methods=['GET'])
    def predictTopicsForNewLearningObjects():
        
        # Finds all Learning Objects that do not have a topic
        learning_objects_without_topic = get_learning_objects_without_topic()

        # Determines which Learning Object belong in an existing topic
        # and which belong in a new topic
        predicted_learning_object_placements = determine_learning_object_placements(learning_objects_without_topic)

        new_topic_learning_objects = []
        standard_topic_learning_objects = {}
        
        for learning_object_cuid in predicted_learning_object_placements:
            if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') == -1:
                new_topic_learning_objects.append(predicted_learning_object_placements[learning_object_cuid])
            else:
                if predicted_learning_object_placements.get(learning_object_cuid).get('topic_id') in standard_topic_learning_objects:
                    standard_topic_learning_objects[topics[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')]].append(predicted_learning_object_placements[learning_object_cuid].get('learning_object'))
                else:
                    standard_topic_learning_objects[topics[predicted_learning_object_placements.get(learning_object_cuid).get('topic_id')]] = [predicted_learning_object_placements[learning_object_cuid].get('learning_object')]

        new_topic_learning_objects = generate_new_topics(new_topic_learning_objects)

        # Each of these Learning Objects are then passed through
        # a cluster of classification models. Each model will return
        # an array probabilities, indicating a confidence that the
        # speficied Learning Object belongs in a topic.

        return jsonify({'standard_topics': standard_topic_learning_objects, 'new_topics': new_topic_learning_objects }), 200


    @app.route('/topics/assign', methods=['POST'])
    def assignNewTopics():
        req_data = request.get_json()
        # topic_assignments = req_data['assignments']
        print(req_data)

        # Check pipeline status
        # If pipeline is currently in progress, tell the client and exit

        # Else, update pipeline status to lock future requests and continue

        # Get list of topic names 
        new_topic_names = list(req_data.keys())
        topic_names = get_all_topic_names()

        # # Compare list of topic names with topic names in given assignment map
        # # Upsert topic names into the topic names list
        for new_name in new_topic_names:

            new_name_exists = False

            for existing_name in topic_names:
                if existing_name.lower() == new_name.lower():
                        new_name_exists = True

            if not new_name_exists:
                topic_names.append(new_name)

        # # Save new topic names list
        update_topic_name_list(topic_names)

        # # Update each Learning Object topic label

        # # Invoke Pipeline (CodeBuild)

        # return jsonify({'topic_names': topic_names }), 200

